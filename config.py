import os
from private import Private
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 设置秘钥预防CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this key was created by GarryLin-w'
    # 配置SMTP服务器信息
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # 配置批处理邮件设置
    FLASK_MAIL_SUBJECT_PREFIX = '[SmartFinancialManager]'  # 主题前缀
    FLASK_MAIL_SENDER = 'SmartFinancialManager Admin <515337036@qq.com>'  # 发送者信息
    FLASK_ADMIN = 'zhuiyiyydyy@163.com'  # 管理员地址
    # 配置数据库信息
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getcwd() + '/app/static/avatar/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # 配置邮箱用户信息
    MAIL_USERNAME = Private.MAIL_USERNAME
    MAIL_PASSWORD = Private.MAIL_PASSWORD
    # 配置数据库信息
    SQLALCHEMY_DATABASE_URI = Private.SQLALCHEMY_DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://'


# 在程序工厂函数根据需要导入对应的配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
