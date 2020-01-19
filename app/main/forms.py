# flask扩展 WTForms-处理web表单
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..dbmodels import Role, User


# 社交系统-文章发布表单
class PostForm(FlaskForm):
    body = PageDownField("您的想法是?", validators=[DataRequired()])
    submit = SubmitField('确认')


# 社交系统-评论表单
class CommentForm(FlaskForm):
    body = StringField('输入您的评论', validators=[DataRequired()])
    submit = SubmitField('确认')
