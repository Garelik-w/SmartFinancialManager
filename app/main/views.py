from flask import render_template, abort, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..dbmodels import User, Role
from .. import db
from ..decorators import admin_required
from .forms import EditProfileForm, EditProfileAdminForm
from . import main  # 导入蓝本对象

# Home页
@main.route('/')
def home():
    return render_template('home.html')


# 资料编辑器-用户资料页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


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
        flash('Your profile has been updated.')
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
        flash('The profile has been updated.')
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
