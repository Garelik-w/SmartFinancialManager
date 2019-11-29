# flask扩展 WTForms-处理web表单
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..dbmodels import Role, User


# 资料编辑器-普通用户表单
class EditProfileForm(FlaskForm):
    name = StringField('昵称', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('介绍')
    avatar = FileField('头像')
    submit = SubmitField('确认')


# 资料编辑器-管理员用户表单
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
    name = StringField('昵称', validators=[Length(0, 64)])
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


# 社交系统-文章发布表单
class PostForm(FlaskForm):
    body = PageDownField("您的想法是?", validators=[DataRequired()])
    submit = SubmitField('确认')


# 社交系统-评论表单
class CommentForm(FlaskForm):
    body = StringField('输入您的评论', validators=[DataRequired()])
    submit = SubmitField('确认')
