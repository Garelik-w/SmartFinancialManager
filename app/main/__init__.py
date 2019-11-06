# 从FLASK模块导入蓝本Blueprint类
from flask import Blueprint

# 蓝本类实例，第一个参数是自定义的蓝本名字（用以确定蓝本路由的作用域）
main = Blueprint('main', __name__)

# 从web包中导入views和errors和两个蓝本路由
from . import views, errors
from ..dbmodels import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)