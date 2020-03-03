from flask import render_template, abort, redirect, url_for, flash, request, current_app, make_response
from flask_login import login_required, current_user
from ..dbmodels import Permission, User, Role, Post, Comment
from .. import db
from ..decorators import admin_required, permission_required
from .forms import PostForm, CommentForm
from . import main  # 导入蓝本对象

# ------------------------------------- 起始页前台 ------------------------------------- #
# Home页
@main.route('/', methods=['GET', 'POST'])
def home():
    form = PostForm()
    if current_user.can(Permission.BACKEND) and form.validate_on_submit():
        # POST && PERMMiSS
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home'))
    # GET
    # 暂时只挑选所有关注者的第一个
    social_admin = current_user
    if current_user.can(Permission.BASIC):
        social_admin_id = current_user.followed.filter_by().first().followed_id
        social_admin = User.query.filter_by(id=social_admin_id).first_or_404()
    # 判断是否只显示关注的用户的文章
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    # 获取分页对象实现分页处理
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('home.html', form=form, posts=posts, social_admin=social_admin,
                           show_followed=show_followed, pagination=pagination)


# ------------------------------------- 社区前后台 ------------------------------------- #
# 社区后台
@main.route('/social_backend/<username>')
def social_backend(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # 获取文章列表，按时间戳排序，并用分页技术处理
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('social-backend.html', user=user, posts=posts,
                           pagination=pagination)


# 社区前台
# 还需要一个装饰器限制必须有关注用户
# 装饰器实现社区条件准入。装饰器由问题，暂时不搞
@permission_required(Permission.FRONTEND)
# @social_required(current_user)
@main.route('/social/<username>')
def social_frontend(username):
    social_admin = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(social_admin):
        return "您已被踢出社区，请联系社区管理员"

    page = request.args.get('page', 1, type=int)
    # 获取文章列表，按时间戳排序，并用分页技术处理
    pagination = social_admin.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('social.html', social_admin=social_admin, posts=posts,
                           pagination=pagination)


# # flask 导入上下文对象和必备函数
# from flask import render_template, session, redirect, url_for, current_app, request, abort
# from datetime import datetime
# from .. import db
# from ..dbmodels import User
# from ..email import send_email
# from . import main  # 导入蓝本对象
# from .forms import NameForm  # 导入web表单模型

# # Index索引页
# @main.route('/index', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)  # 插入数据
#             db.session.add(user)
#             db.session.commit()
#             session['known'] = False
#             if current_app.config['FLASK_ADMIN']:
#                 send_email(current_app.config['FLASK_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         return redirect(url_for('main.index'))
#     return render_template('index.html',
#                            form=form, name=session.get('name'),
#                            known=session.get('known', False),
#                            current_time=datetime.utcnow())
