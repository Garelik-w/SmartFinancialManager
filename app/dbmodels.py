from werkzeug.security import generate_password_hash, check_password_hash  # 导入加密函数和验证函数
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
from . import db, login_manager
from markdown import markdown
import bleach

# 权限管理（位操作）
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


# 数据库角色模型(表）
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
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
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


# 数据库用户模型（表）
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户资料-注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户资料-上次登录时间
    user_avatar = db.Column(db.String(128), default=None)  # 用户头像
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # 关联POST模型的外键

    # 初始化
    # 赋予角色（普通用户使用默认角色，管理员则为Administrator）
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # 将password函数转为属性，通过werkzeug实现加密
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 用户管理-验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户注册-创建确认令牌，过期时间为60min
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')  # 加密信息confirm

    # 用户注册-检验令牌，并和已登录用户匹配
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

    # 忘记密码-生成重置密码确认令牌（用于忘记密码确认）
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')  # 加密信息reset

    # 忘记密码-重置密码（需要有密令）
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

    # 修改邮箱-创建确认令牌
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    # 修改邮箱-实现邮箱修改
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

    # 权限管理-检查用户权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # 权限管理-判断是否是管理员
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # 获取最新时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 生成假用户数据
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
                     name=fake.name(),
                     location=fake.city(),
                     about_me=fake.text(),
                     member_since=fake.past_date())
            db.session.add(u)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User %r>' % self.username


# 权限管理-继承Flask-Login提供的匿名基类
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# 权限管理-匿名用户默认权限
login_manager.anonymous_user = AnonymousUser


# 绑定login_manger登录函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 文章发布模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)  # Markdown文本缓存
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键定义，关联users表的id

    # 将body字段保存的Markdown纯文本转换成html并存储在body_html
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

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


# SQLAlchemy的set事件监听：只要实例的Body值设了新值，就会调用函数
db.event.listen(Post.body, 'set', Post.on_changed_body)
