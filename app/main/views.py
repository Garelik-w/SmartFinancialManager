# flask 导入上下文对象和必备函数
from flask import render_template, session, redirect, url_for, current_app, request
from datetime import datetime
from .. import db
from ..dbmodels import User
from ..email import send_email
from . import main  # 导入蓝本对象
from .forms import NameForm  # 导入web表单模型

# Home页
@main.route('/')
def home():
    return render_template('home.html')

# Index索引页
@main.route('/index', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)  # 插入数据
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASK_ADMIN']:
                send_email(current_app.config['FLASK_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('main.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())
