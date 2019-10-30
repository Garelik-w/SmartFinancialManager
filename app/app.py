#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/10/24:15:26
# email:515337036@qq.com
# =====================

from datetime import datetime
from flask import Flask, render_template
# flask 导入上下文对象和必备函数
from flask import request, session, redirect, url_for, flash
# flask扩展 Bootstrap
from flask_bootstrap import Bootstrap
# flask扩展 Moment
from flask_moment import Moment
# flask扩展 WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
# 设置秘钥预防CSRF
app.config['SECRET_KEY'] = 'this key was created by GarryLin-w'

bootstrap = Bootstrap(app)
moment = Moment(app)

# 表单
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Home页
@app.route('/', methods=['GET', 'POST'])
def home():
    form = NameForm()
    if form.validate_on_submit():
        # POST
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('home'))
    # GET
    return render_template('home.html',
                           form=form, name=session.get('name'),
                           current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

# 错误信息页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 留着这两个原始结构（不调用bootstrap，不继承任何基模板）
@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        return render_template('signin-ok.html', username=username)
    return render_template('form.html', message='Bad username or password', username=username)


if __name__ == '__main__':
    app.run()
