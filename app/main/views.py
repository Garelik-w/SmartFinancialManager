from flask import render_template, abort, redirect, url_for, flash, request, current_app, make_response
from flask_login import login_required, current_user
from ..dbmodels import Permission, User, Role, Post, Comment
from .. import db
from ..decorators import admin_required, permission_required
from .forms import PostForm, CommentForm
from . import main  # 导入蓝本对象
from flask_sqlalchemy import get_debug_queries


# 测试系统-查询超时记录
# 在main脚本路由请求结束后执行
@main.after_app_request
def after_request(response):
    # get_debug_queries 获取当前路由请求的所有查询元素
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


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
    return render_template('home.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


# 用户系统-后台中心
@main.route('/backend/<username>')
def backend(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # 获取文章列表，按时间戳排序，并用分页技术处理
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


# 测试系统-关闭web服务器
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


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
