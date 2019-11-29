#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:18:39
# email:515337036@qq.com
# ======================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..dbmodels import User


# 用户管理-登录表单（用户名是邮箱，且提供记住功能）
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


# 用户管理-注册表单
class RegistrationForm(FlaskForm):
    email = StringField('邮箱地址', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名只能有字母、数字、点或下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须一致.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经被注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被占用！.')


# 用户管理-修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧的密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认新密码',
                              validators=[DataRequired()])
    submit = SubmitField('确认修改')


# 忘记密码-输入邮箱地址重设的表单
class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱地址', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


# 忘记密码-密码重设表单
class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


# 用户管理-修改邮箱表单
class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱地址', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('您的密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经被注册.')
