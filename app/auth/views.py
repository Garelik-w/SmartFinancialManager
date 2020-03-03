#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:17:41
# email:515337036@qq.com
# ======================

from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..dbmodels import User, Post, Role, Permission
from ..label.labelmodels import Label
from ..email import send_email
from .forms import LoginForm, NormalRegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm,\
    ChangeEmailForm, EditProfileForm, EditProfileAdminForm, FansRegistrationForm, FansLoginForm, \
    SupplyFansRegistrationForm
from ..decorators import admin_required, permission_required


# auth蓝本请求前检查
@auth.before_app_request
def before_request():
    # 检查已登录且未认证用户，跳转到未认证提示界面
    # 优先判断粉丝临时登陆，那么检查临时令牌是否过期，过期了就拦截
    # 符合条件则拦截：用户已登录 && 用户账户未确认 && 请求端点不在认证蓝本中
    # 最新访问时间更新
    # not current_user.confirmed and
    if current_user.is_authenticated:
        # 更新用户状态
        current_user.ping()
        # 唯有未认证且超时的情况需要进入认证界面
        if current_user.confirmed is False and current_user.confirm_social_token(current_user.tmp_token) is False:
            is_confirmed = False
        else:
            is_confirmed = True

        if not is_confirmed \
            and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

# ------------------------------------ 用户系统常规功能 ------------------------------------ #
# 注册：大V用户和普通用户注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = NormalRegistrationForm()
    if form.validate_on_submit():
        # POST
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # 生成确认密令并发送邮件
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('一封新的认证邮件已经发往您的邮箱.')
        return redirect(url_for('main.home'))
    # GET
    return render_template('auth/register.html', form=form)


# 注册：粉丝简易注册
@auth.route('/fans_register/<token>', methods=['GET', 'POST'])
def fans_register(token):
    form = FansRegistrationForm()
    if form.validate_on_submit():
        # POST
        user = User(username=form.username.data,
                    source=form.source.data)
        db.session.add(user)
        db.session.commit()
        # 解析token,成功返回大V的id,获取这个id的user
        admin_id = user.parser_social_token(token)
        try:
            admin = User.query.filter_by(id=admin_id).first()
        except:
            admin_id = False
        if not admin_id:
            flash('您的链接已过期，请重新申请加入。')
            return redirect(url_for('main.home'))
        # 生成保存一个临时的Token作为临时登陆权限。
        user.tmp_token = user.generate_social_temp_confirmation()
        db.session.add(user)
        # 关注大V表示加入社区
        user.follow(admin)
        user.insert_label()
        db.session.commit()
        flash('您已成功加入社区.')
        return redirect(url_for('main.home'))
    # GET
    return render_template('auth/fans_register.html', form=form)

# 登录-粉丝用户登录页面
@auth.route('/fans_login', methods=['GET', 'POST'])
def fans_login():
    form = FansLoginForm()
    if form.validate_on_submit():
        # POST
        user = User.query.filter_by(username=form.username.data.lower()).first()
        # 判断粉丝是否存在，且临时认证是否到期
        if user is not None:
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.home')
            return redirect(next)
        flash('不存在该粉丝用户或已认证,请重新选择登陆方式!')
    # GET
    return render_template('auth/fans_login.html', form=form)

# 用户认证管理-大V/普通用户未认证、临时粉丝超时补充注册
@auth.route('/unconfirmed', methods=['GET', 'POST'])
def unconfirmed():
    # 游客或已认证用户直接返回
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    # return render_template('auth/unconfirmed.html')
    form = SupplyFansRegistrationForm()
    if form.validate_on_submit():
        # POST
        current_user.email = form.email.data
        current_user.password = form.password.data
        if form.phone is not None:
            current_user.phone = form.phone.data
        # 认证用户
        current_user.confirmed = True
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('main.home'))
    # GET
    flash('粉丝账户已过期，请补充信息用以认证!')
    return render_template('auth/supply_register.html', form=form)


# 用户注册-未认证用户重新发送邮件确认
# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
#     token = current_user.generate_confirmation_token()
#     send_email(current_user.email, 'Confirm Your Account',
#                'auth/email/confirm', user=current_user, token=token)
#     flash('一个新的认证邮件已经发往您的邮箱.')
#     return redirect(url_for('main.home'))


# 用户管理-普通用户/大V登录页面
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # POST
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.home')
            return redirect(next)
        flash('不存在用户或者密码错误.')
    # GET
    return render_template('auth/login.html', form=form)

# 用户管理-登出页面
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出登录.')
    return redirect(url_for('main.home'))


# 用户邮箱注册认证-确认邮箱令牌URL
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    # current_user实质是注册创建的user对象，调用其confirm方法
    if current_user.confirm(token):
        db.session.commit()
        flash('您的账户已经认证. 欢迎您!')
    else:
        flash('这个认证链接不存在或者已经失效，请重新认证.')
    return redirect(url_for('main.home'))


# 用户管理-修改密码页面
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # POST
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('您的密码已经更新.')
            return redirect(url_for('main.home'))
        else:
            flash('不存在密码.')
    # GET
    return render_template("auth/change_password.html", form=form)


# 忘记密码-请求重设页面
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.home'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        # POST
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # 如果存在邮箱
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('一封认证身份的邮件已经发往您的邮箱.')
        return redirect(url_for('auth.login'))
    # GET
    return render_template('auth/reset_password.html', form=form)


# 忘记密码-确认令牌URL
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.home'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # 重置密码
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('您的密码已更新.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.home'))
    return render_template('auth/reset_password.html', form=form)


# 用户管理-修改邮箱页面
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # POST
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封认证身份的邮件已经发往您的邮箱.')
            return redirect(url_for('main.home'))
        else:
            flash('不存在该邮箱或者密码错误.')
    # GET
    return render_template("auth/change_email.html", form=form)


# 邮箱修改-确认令牌URL
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    # 修改邮箱
    if current_user.change_email(token):
        db.session.commit()
        flash('您的邮箱已经修改.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.home'))


# ------------------------------------ 普通用户的前台&后台 ------------------------------------ #
# 用户系统-用户中心页面(普通用户前台）
@auth.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # label = Label.query.filter_by()
    page = request.args.get('page', 1, type=int)
    # 获取文章列表，按时间戳排序，并用分页技术处理
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


# ------------------------------------ 普通用户的后台 ------------------------------------ #
# 用户系统-普通用户编辑资料(普通用户后台）
@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # POST
        current_user.nickname = form.nickname.data
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
            return redirect(url_for(auth.user_profile), username=current_user.username)
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.username, fname))
        current_user.user_avatar = '/static/avatar/{}_{}'.format(current_user.username, fname)
        # 提交并更新数据库
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('您的自我介绍已经被修改。')
        return redirect(url_for('auth.user_profile', username=current_user.username))
    # GET
    form.nickname.data = current_user.nickname
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 用户系统-管理员用户资料编辑(可修改邮箱等关键信息）
@auth.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
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
        user.name = form.nickname.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('您的自我介绍已经被修改。')
        return redirect(url_for('auth.user_profile', username=user.username))
    # GET
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.nickname.data = user.nickname
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


