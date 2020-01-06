# 以FLASK作为WEB架构
from flask import Flask
# flask扩展 Bootstrap-模板开源框架（强大的模板设计）
from flask_bootstrap import Bootstrap
# flask扩展 Moment模块-本地化日期和时间
from flask_moment import Moment
# flak扩展 Mail电子邮件
from flask_mail import Mail
# 从配置文件导入配置（数据库、邮箱信息等）
from config import config
# flask扩展 SQLAlchemy-数据库ORM框架
from flask_sqlalchemy import SQLAlchemy
# flask扩展 Login用户认证状态管理
from flask_login import LoginManager
# flask扩展 PageDown-富文本Markdown技术
from flask_pagedown import PageDown
# 导入mysqlDB用以在SQLAlchemy框架下配置MySQL
import pymysql
pymysql.install_as_MySQLdb()

# 各模块实例
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

# 用户认证状态管理
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'


# 程序工厂函数（flask实例并初始化各模块）
def create_app(config_name):
    app = Flask(__name__)
    # 从配置文件导入配置信息给app对象（如果配置文件里有做初始化则执行）
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 各个扩展模块初始化
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 导入注册main蓝本路由
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 导入注册auth蓝本路由
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # 设置增加蓝本路由的前缀

    # 导入注册api蓝本路由
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    # # 导入注册VipAdmin蓝本路由
    # from .vipAdmin import vipAdmin as VipAdmin_blueprint
    # app.register_blueprint(VipAdmin_blueprint, url_prefix='/Vip')

    return app

