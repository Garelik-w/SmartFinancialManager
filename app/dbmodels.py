from werkzeug.security import generate_password_hash, check_password_hash  # 导入加密函数和验证函数
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from datetime import datetime, timedelta
from . import db, login_manager
from markdown import markdown
import bleach
from app.exceptions import ValidationError
from .label.labelmodels import Label


# 用户系统-权限管理（位操作）
# 1.基础功能（包括用户前后台、查看私信等功能）
# 2.社区前台
# 3.工具箱：一键复盘
# 4.工具箱：深度分析
# 5.工具箱：一键策略生成
# 6.社区市场
# 7.社区后台
# 8.标签系统
# 9.工具箱：后期扩展
# 10.开发者权限
class Permission:
    BASIC = 1
    FRONTEND = 2
    TOOLBOX_REPLAY = 4
    TOOLBOX_ANALYSIS = 8
    TOOLBOX_GENERATE = 16
    MARKET = 32
    BACKEND = 64
    LABEL = 128
    TOOLBOX_EX = 256
    DEVELOPER = 512


# 社交系统-关联表模型（社交关注系统）
class Follow(db.Model):
    __tablename__ = 'follows'
    # 粉丝
    fans_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # 关注的人
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 用户系统-数据库角色模型(表）
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    # 数据库表单操作-更新Role数据库表信息为本flask程序的
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.BASIC, Permission.FRONTEND],
            'VipUser': [Permission.BASIC, Permission.FRONTEND, Permission.TOOLBOX_REPLAY,
                        Permission.TOOLBOX_ANALYSIS, Permission.MARKET],
            'SuperVipAdmin': [Permission.BASIC, Permission.FRONTEND, Permission.TOOLBOX_REPLAY,
                              Permission.TOOLBOX_ANALYSIS, Permission.TOOLBOX_GENERATE, Permission.MARKET,
                              Permission.BACKEND, Permission.LABEL],
            'Developer': [Permission.BASIC, Permission.FRONTEND, Permission.TOOLBOX_REPLAY,
                          Permission.TOOLBOX_ANALYSIS, Permission.TOOLBOX_GENERATE, Permission.MARKET,
                          Permission.BACKEND, Permission.LABEL, Permission.TOOLBOX_EX,
                          Permission.DEVELOPER],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    # 数据库表单操作-增加权限
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    # 数据库表单操作-移除权限
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    # 数据库表单操作-重置权限
    def reset_permissions(self):
        self.permissions = 0

    # 数据库表单操作-权限设置
    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


# 用户系统-数据库用户模型（表）
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    tmp_token = db.Column(db.Text)
    nickname = db.Column(db.String(64))
    source = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    phone = db.Column(db.String(11), unique=True, index=True)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户资料-注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户资料-上次登录时间
    user_avatar = db.Column(db.String(128), default=None)  # 用户头像
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # 关联POST模型的外键
    labels = db.relationship('Label', backref='user', lazy='dynamic')  # 关联LABEL模型的外键
    analysis = db.relationship('Analysis', backref='user', lazy='dynamic')  # 关联POST模型的外键

    # 社交系统-关注的人
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.fans_id],
                               backref=db.backref('fans', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # 社交系统-粉丝（关注我的人）
    fans = db.relationship('Follow',
                           foreign_keys=[Follow.followed_id],
                           backref=db.backref('followed', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')
    # 社交系统-评论（一对多关系类型）
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # 初始化
    # 赋予角色（这里的role是Role模型的反向代理，在User模型操作Role模型）
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(name='Developer').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # 创建基础标签
    # 需要明确标签从属于哪个大V的社区
    def insert_basic_label(self, idol_id, basic_id=1, is_view=False, is_limit=False):
        # 如果标签已经存在，那么增加新的关系表(需要明确大V社区)
        label = self.labels.filter(Label.user_id == self.id, Label.idol_id == idol_id).first()
        if label is not None:
            label.generate_basic_relation(basic_id=basic_id, is_view=is_view, is_limit=is_limit)
        else:
            # 如果标签不存在，那么标签初始化
            label = Label(user_id=self.id, idol_id=idol_id)
            # 给标签创建关系表，关联基础标签
            label.generate_basic_relation(basic_id=basic_id, is_view=is_view, is_limit=is_limit)
        db.session.add(label)

    # 用户升级或降级VIP
    def set_vip(self, idol_id, target=False):
        label = self.labels.filter(Label.user_id == self.id, Label.idol_id == idol_id).first()
        if label is not None:
            label.set_object_vip(target)
        else:
            # 如果没有生成标签，那就自动创建一个
            label = Label(user_id=self.id, idol_id=idol_id)
            label.set_object_vip(target)
        db.session.add(label)

    # 用户系统-加密：将password函数转为属性，通过werkzeug实现加密
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 用户系统-验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户系统-大V/普通用户注册：创建确认令牌，过期时间为60min
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')  # 加密信息confirm

    # 用户系统-大V/普通用户注册：检验令牌，并和已登录用户匹配
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)  # 只添加修改到会话，需要在confirm视图函数确认提交
        return True

    # 用户系统：生成社区加入链接（1个月的有效期：2592000）
    def generate_social_token_link(self, expiration=2592000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'social': self.id}).decode('utf-8')
        return url_for('auth.fans_register', token=token, _external=True)

    # 用户系统-粉丝社区链接解析：解析Token并返回解析结果
    def parser_social_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 如果秘钥到期那么会获取失败
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        data = data.get('social')
        if User.query.get(data) is None:
            return False
        db.session.add(self)
        return data
        # user_id = data.get('social')
        # if User.query.get(user_id) is None or user_id == self.id:
        #     return False
        # try:
        #     user = User.query.filter_by(id=user_id).first()
        #     self.follow(user)
        # except:
        #     return False
        # db.session.add(self)
        # return True

    # 用户系统：生成粉丝临时身份证(临时身份6H）
    def generate_social_temp_confirmation(self, expiration=21600):
        return self.generate_confirmation_token(expiration)

    # 用户系统-粉丝临时身份认证：认证临时Token是否过期，不会修改confirmed的值
    def confirm_social_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 如果过期则会报错
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        db.session.add(self)
        return True

    # 用户系统-忘记密码：生成重置密码确认令牌（用于忘记密码确认）
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')  # 加密信息reset

    # 用户系统-忘记密码：重置密码（需要有密令）
    # 静态方法，不可访问类属性和方法，可被类和实例调用
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # 用户系统-修改邮箱：创建确认令牌
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    # 用户系统-修改邮箱：实现邮箱修改
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    # 用户系统-权限管理：检查用户权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # 用户系统-权限管理：判断是否是开发者(主要模板中用）
    def is_developer(self):
        return self.can(Permission.DEVELOPER)

    # 用户系统-权限管理：判断是否是大V管理员(主要模板中用）
    def is_supervipadmin(self):
        return self.can(Permission.BACKEND)

    # 更新用户状态
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 用户系统-关注指定用户
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(fans=self, followed=user)
            db.session.add(f)

    # 用户系统-取消关注指定用户
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    # 用户系统-查询指定用户是否是我关注的人
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    # 用户系统-查询指定用户是否是粉丝
    def is_fans(self, user):
        if user.id is None:
            return False
        return self.fans.filter_by(
            fans_id=user.id).first() is not None

    # 文章系统-联结查询-查询所有关注用户的发布文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.fans_id == self.id)

    # API系统：API认证-生成用户密码令牌
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    # API系统：API认证-确认用户密码令牌
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    # API系统：API-JSON资源转换
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user

    # 用户系统：生成假用户数据
    @staticmethod
    def generate_fake_users(count=10):
        from sqlalchemy.exc import IntegrityError
        from faker import Faker
        fake = Faker()
        i = 0
        while i < count:
            u = User(email=fake.email(),
                     username=fake.user_name(),
                     password='password',
                     confirmed=True,
                     nickname=fake.name(),
                     location=fake.city(),
                     about_me=fake.text(),
                     member_since=fake.past_date())
            db.session.add(u)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()

    # 用户系统：创建管理员账户
    @staticmethod
    def generate_admin_user():
        r = Role.query.filter_by(name='Developer').first()
        u = User(email=current_app.config['FLASK_ADMIN'], password='w123456', confirmed=True,
                 username='GarryLin_admin', role=r)
        db.session.add(u)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


# 权限管理-继承Flask-Login提供的匿名基类
class AnonymousUser(AnonymousUserMixin):
    # 提供和user模型一样的接口
    def can(self, permissions):
        return False

    def is_supervipadmin(self):
        return False

    def is_developer(self):
        return False

    def append_analysis_data(self):
        return False


# 权限管理-匿名用户默认权限
login_manager.anonymous_user = AnonymousUser


# 绑定login_manger登录函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 文章系统-文章发布模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)  # Markdown文本缓存
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 多对一关系类型：外键定义，关联users表的id
    # 社交系统-评论（一对多关系类型）
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # 标签系统：文章标签（一对多关系类型）
    labels = db.relationship('Label', backref='post', lazy='dynamic')

    # 创建标签
    def generate_label(self):
        label = Label(post_id=self.id)
        label.generate_basic_relation()
        db.session.add(label)

    # 将body字段保存的Markdown纯文本转换成html并存储在body_html
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    # API-资源转换成成JSON格式
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        return json_post

    # API-读取JSON格式的body
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

    # 生成假文章数据
    @staticmethod
    def generate_fake_posts(count=10):
        from random import randint
        from faker import Faker
        fake = Faker()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=fake.text(),
                     timestamp=fake.past_date(),
                     author=u)
            db.session.add(p)
        db.session.commit()


# 社交系统-评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    # 将body字段保存的Markdown纯文本转换成html并存储在body_html
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    # API-将资源转换成JSON格式
    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
        }
        return json_comment

    # API-读取JSON格式的body
    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


# SQLAlchemy的set事件监听：只要实例的Body值设了新值，就会调用函数
db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# 数据分析存储模型
class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    fans_total = db.Column(db.String(24))
    posts_total = db.Column(db.String(24))
    fans_added = db.Column(db.String(24))  # 新增粉丝数(非净值）
    fans_reduce = db.Column(db.String(24))  # 新增粉丝数(非净值）
    source_wb = db.Column(db.String(24))  # 粉丝来源-微博
    source_jrtt = db.Column(db.String(24))  # 粉丝来源-今日头条
    source_xq = db.Column(db.String(24))  # 粉丝来源-雪球
    source_wx = db.Column(db.String(24))  # 粉丝来源-微信
    source_qq = db.Column(db.String(24))  # 粉丝来源-QQ
    source_others = db.Column(db.String(24))  # 粉丝来源-其他平台
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 多对一关系类型：外键定义，关联users表的id

    # 更新最新一天分析数据数据（每日定时任务调度更新）
    # 如果超过30天，那么删除多出的数据，保证数据库只存放近30天的数据
    @staticmethod
    def append_analysis_data(user_id):
        user = User.query.filter_by(id=user_id).first()
        myfans = user.fans  # 获取用户的粉丝过滤器
        # 插入新数据，而不是更新旧数据
        data = Analysis(user_id=user_id)
        data.fans_total = user.fans.count()
        data.posts_total = user.posts.count()
        # 找出今日关注大V的粉丝(就是新增粉丝)
        data.fans_added = myfans.filter(Follow.timestamp > (datetime.utcnow() - timedelta(days=1))).count()
        # 计算今日新减粉丝(今日总粉丝-昨日总粉丝-今日新增粉丝)
        data.fans_reduce = data.fans_total - int(user.analysis.order_by(Analysis.timestamp.desc()).all()[1].fans_total) - data.fans_added
        # 计算保存粉丝来源
        fans_source = [User.query.filter_by(id=fans.fans_id).first().source for fans in myfans]
        data.source_wb = fans_source.count('Wb')
        data.source_jrtt = fans_source.count('Jrtt')
        data.source_xq = fans_source.count('Xq')
        data.source_wx = fans_source.count('Wx')
        data.source_qq = fans_source.count('Qq')
        data.source_others = fans_source.count('Others') + fans_source.count('Zsxq') + fans_source.count('Personal')
        data.timestamp = datetime.utcnow()
        db.session.add(data)
        return data

    # 生成n天假数据(仅测试用）
    @staticmethod
    def generate_fake_datas(count=10):
        from random import randint
        from faker import Faker
        fake = Faker('zh_CN')
        # 遍历每个用户，只针对大V生成假数据
        for user in User.query.all():
            if user.is_supervipadmin():
                # 清空每个用户超过30天的数据
                del_date = datetime.utcnow() - timedelta(days=31)
                del_data = Analysis.query.filter(Analysis.timestamp < del_date).all()
                [db.session.delete(f) for f in del_data]
                # 遍历今日起的过去30天，并插入每天的假数据
                for day in range(count, 0, -1):
                    get_date = datetime.utcnow() - timedelta(days=day)
                    fake_data = Analysis(user_id=user.id, timestamp=get_date)
                    fake_data.fans_total = fake.random_number()
                    fake_data.posts_total = fake.random_number()
                    fake_data.fans_added = fake.random_number()
                    fake_data.fans_reduce = fake.random_number()
                    db.session.add(fake_data)
                db.session.commit()















