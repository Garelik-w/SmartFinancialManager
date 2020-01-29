from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError


# 登录表单：普通/大V用户登录表单
class LabelPermissionForm(FlaskForm):
    # 可以自由选择是以邮箱还是手机号登录
    is_vip = BooleanField('vip')
    submit = SubmitField('确认')