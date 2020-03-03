import os
try:
    from private import Private
except ImportError:
    class Private(object):
        MAIL_USERNAME = ''
        MAIL_PASSWORD = ''
        SQLALCHEMY_DEVELOP_DATABASE_URI = ""
        SQLALCHEMY_TEST_DATABASE_URI = ""

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
    FLASK_ADMIN = 'zhuiyiyydyy@163.com'  # 管理员地址
    # 配置数据库信息
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getcwd() + '/app/static/avatar/'  # 头像上传路径
    # 设置分页显示信息
    FLASK_POSTS_PER_PAGE = 20
    FLASK_FOLLOWERS_PER_PAGE = 50
    FLASK_COMMENTS_PER_PAGE = 30
    # 缓慢查询的超时设置
    SQLALCHEMY_RECORD_QUERIES = True  # 允许在生产环境下使用
    FLASK_SLOW_DB_QUERY_TIME = 0.5  # 查询超时时间0.5s

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # 配置邮箱用户信息
    MAIL_USERNAME = Private.MAIL_USERNAME
    MAIL_PASSWORD = Private.MAIL_PASSWORD
    FLASK_MAIL_SENDER = 'SmartFinancialManager Admin <515337036@qq.com>'  # 发送者信息
    # 配置数据库信息
    SQLALCHEMY_DATABASE_URI = Private.SQLALCHEMY_DEVELOP_DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # 禁用flask-WTF的CSRF
    FLASK_MAIL_SENDER = 'SmartFinancialManager Admin <515337036@qq.com>'  # 发送者信息
    # 配置数据库信息
    SQLALCHEMY_DATABASE_URI = Private.SQLALCHEMY_TEST_DATABASE_URI


class ProductionConfig(Config):
    # 配置数据库信息
    try:
        SQLALCHEMY_DATABASE_URI = Private.SQLALCHEMY_PRODUCTION_DATABASE_URI
    except:
        SQLALCHEMY_DATABASE_URI = "mysql://root:w123456@49.235.42.145:3306/production-db"
    # 配置邮箱用户信息
    MAIL_USERNAME = '515337036@qq.com'  # 这里我需要修改
    MAIL_PASSWORD = 'xfiuzbwzliicbjcf'
    FLASK_MAIL_SENDER = 'SmartFinancialManager Admin <515337036@qq.com>'  # 发送者信息
    # 配置scheduler调度器
    SCHEDULER_API_ENABLE = True

    # 部署-日志记录器
    # @classmethod
    # def init_app(cls, app):
    #     Config.init_app(app)
    #
    #     # email errors to the administrators
    #     import logging
    #     from logging.handlers import SMTPHandler
    #     credentials = None
    #     secure = None
    #     if getattr(cls, 'MAIL_USERNAME', None) is not None:
    #         credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
    #         if getattr(cls, 'MAIL_USE_TLS', None):
    #             secure = ()
    #     # 基于SMTP简单邮件协议服务器发送邮件
    #     mail_handler = SMTPHandler(
    #         mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
    #         fromaddr=cls.FLASK_MAIL_SENDER,
    #         toaddrs=[cls.FLASK_ADMIN],
    #         subject=cls.FLASK_MAIL_SUBJECT_PREFIX + ' Application Error',
    #         credentials=credentials,
    #         secure=secure)
    #     mail_handler.setLevel(logging.ERROR)
    #     app.logger.addHandler(mail_handler)


# 在程序工厂函数根据需要导入对应的配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
