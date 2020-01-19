#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:18:39
# email:515337036@qq.com
# ======================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..dbmodels import User, Role


# 登录表单：普通/大V用户登录表单
class LoginForm(FlaskForm):
    # 可以自由选择是以邮箱还是手机号登录
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


# 登录表单：粉丝登录表单
class FansLoginForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名只能有字母、数字、点或下划线')])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


# 注册表单：简易粉丝注册表单
class FansRegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名只能有字母、数字、点或下划线')])
    my_choices = [('Xq', '雪球'), ('Wb', '新浪微博'), ('Zsxq', '知识星球'),
                  ('Qq', 'QQ等社群'), ('Jrtt', '今日头条'),  ('Wx', '微信公众号'), ('Personal', '个人渠道'),
                  ('Others', '其他财经平台')]
    channel = SelectField(choices=my_choices, default=['Choice_xq'], label='加入渠道')
    submit = SubmitField('加入社区')


# 注册表单：建议粉丝补充注册表单：
# 注册表单：简易粉丝注册表单
class SupplyFansRegistrationForm(FlaskForm):
    email = StringField('邮箱地址', validators=[DataRequired(), Length(1, 64),
                                            Email()])
    phone = StringField('手机号', validators=[Length(11)])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须一致.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    # FlaskForm这个类会识别“validate_”这个字符后面的字段，用来做对应的验证函数
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经被注册.')

    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).first():
            raise ValidationError('手机号已经被占用！.')


# 注册表单:普通用户注册表单
class NormalRegistrationForm(FlaskForm):
    email = StringField('邮箱地址', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名只能有字母、数字、点或下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须一致.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # FlaskForm这个类会识别“validate_”这个字符后面的字段，用来做对应的验证函数
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经被注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被占用！.')


# 注册表单:大V用户注册表单
class SuperVipRegistrationForm(FlaskForm):
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


# ------------------------------------ 普通用户的后台 ------------------------------------ #
# 用户系统-普通用户表单
class EditProfileForm(FlaskForm):
    nickname = StringField('昵称', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('介绍')
    avatar = FileField('头像')
    submit = SubmitField('确认')


# 用户系统-开发者用户表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('邮件', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('确认')
    role = SelectField('权限', coerce=int)
    nickname = StringField('昵称', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('介绍')
    avatar = FileField('头像')
    submit = SubmitField('确认')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


# 用户系统-用户信息表单
class NameForm(FlaskForm):
    name = StringField('您的昵称是?', validators=[DataRequired()])
    submit = SubmitField('确认')
