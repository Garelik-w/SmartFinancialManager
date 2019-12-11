#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:17:41
# email:515337036@qq.com
# ======================

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..dbmodels import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm,\
    ChangeEmailForm


# auth蓝本请求前检查
@auth.before_app_request
def before_request():
    # 用户注册-检查已登录且未认证用户，跳转到未认证提示界面
    # 用户注册-符合条件则拦截：用户已登录 && 用户账户未确认 && 请求端点不在认证蓝本中
    # 用户资料-最新访问时间更新
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


# 用户注册-用户未认证页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('auth/unconfirmed.html')


# 用户注册-未认证用户重新发送邮件确认
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('一个新的认证邮件已经发往您的邮箱.')
    return redirect(url_for('main.home'))


# 用户管理-登录页面
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


# 用户注册-注册页面
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
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


# 用户注册-确认令牌URL
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