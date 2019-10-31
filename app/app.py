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
# flask扩展ORM框架SQLAlchemy（配置mysql）
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
# flask扩展 Script命令行
from flask_script import Manager
# flask扩展 Migrate数据库迁移工具
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)  # flask初始化
# 设置秘钥预防CSRF
app.config['SECRET_KEY'] = 'this key was created by GarryLin-w'
# 配置数据库路径
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:123456@localhost:3306/flask-db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化
bootstrap = Bootstrap(app)  # flask-bootstrap初始化
moment = Moment(app)  # flask-moment初始化
db = SQLAlchemy(app)  # flask-SQLAlchemy初始化
manager = Manager(app)  # flask-script初始化
migrate = Migrate(app, db)  # flask-Migrate初始化

# 数据库模型(表）
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

# 表单模型
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Home页
@app.route('/', methods=['GET', 'POST'])
def home():
    form = NameForm()
    if form.validate_on_submit():
        # POST
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('home'))
    # GET
    return render_template('home.html',
                           form=form, name=session.get('name'), known=session.get('known', False),
                           current_time=datetime.utcnow())

# 功能页面
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
    # 需要从request对象读取表单内容，然后和cookie的信息比较
    old_name = session.get('name')
    username = request.form['username']
    password = request.form['password']

    if old_name is not None and old_name != username:
        flash('Looks like you have changed your name!')

    if username == 'admin' and password == 'password':
        return render_template('signin-ok.html', username=username)
    return render_template('form.html', message='Bad username or password', username=username)

# shell命令调试用(flask-script)
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

if __name__ == '__main__':
#     app.run()
    manager.add_command('db', MigrateCommand)
    manager.run()