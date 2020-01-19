# 从FLASK模块导入蓝本Blueprint类
from flask import Blueprint

# 蓝本类实例，第一个参数是自定义的蓝本名字（用以确定蓝本路由的作用域）
main = Blueprint('main', __name__)

# 导入后台系统模块(main）、文章系统模块（posts)、社交系统模块（social)、错误页面
from . import views, errors, posts, social
from ..dbmodels import Permission


# 蓝本模板调用会自动插入词典参数（钩子函数）
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
