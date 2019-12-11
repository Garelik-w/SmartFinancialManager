from flask import render_template, abort, redirect, url_for, flash, request, current_app, make_response
from flask_login import login_required, current_user
from ..dbmodels import Permission, User, Role, Post, Comment
from .. import db
from ..decorators import admin_required, permission_required
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
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
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
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


# 资料编辑器-用户中心页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # 获取文章列表，按时间戳排序，并用分页技术处理
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


# 资料编辑器-普通用户编辑资料
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # POST
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # 用户提交头像
        avatar = request.files['avatar']
        fname = avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
        flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('文件类型错误')
            return redirect(url_for(main.user), username=current_user.username)
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.username, fname))
        current_user.user_avatar = '/static/avatar/{}_{}'.format(current_user.username, fname)
        # 提交并更新数据库
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('您的自我介绍已经被修改。')
        return redirect(url_for('.user', username=current_user.username))
    # GET
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 资料编辑器-管理员用户资料编辑(可修改邮箱等关键信息）
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        # POST
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('您的自我介绍已经被修改。')
        return redirect(url_for('.user', username=user.username))
    # GET
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


# 文本编辑器-文章页面
# 每个文本内容都对应一个URL链接
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        # POST
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('您的评论已经被发布.')
        return redirect(url_for('.post', id=post.id, page=-1))
    # GET
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['FLASK_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


# 文本编辑器-文本内容修改
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章已经成功更新！')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


# 社交系统-功能-关注指定用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户！')
        return redirect(url_for('.home'))
    if current_user.is_following(user):
        flash('您已经关注此用户.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('您已成功关注 %s.' % username)
    return redirect(url_for('.user', username=username))


# 社交系统-功能-取消关注指定用户
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('.home'))
    if not current_user.is_following(user):
        flash('您已经取消关注此用户！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('您已成功取消关注 %s ！' % username)
    return redirect(url_for('.user', username=username))


# 社交系统-查看粉丝的页面
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('.home'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


# 社交系统-查看关注的人的页面
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('.home'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


# 社交系统-功能-显示所有用户的文章
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


# 社交系统-功能-仅显示关注用户的文章
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


# 社交系统-功能-审核用户评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


# 社交系统-功能-审核通过评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


# 社交系统-功能-审核禁止评论
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


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
