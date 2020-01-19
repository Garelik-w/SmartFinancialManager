#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/4:23:31
# email:515337036@qq.com
# ======================


from functools import wraps
from flask import abort
from flask_login import current_user
from .dbmodels import Permission


# ------------------------------ 用户系统权限控制 ------------------------------ #
# 装饰器-权限设置：检查用户权限，如果是没权限返回403错误页面
def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 仅大V管理员可以访问
def admin_required(func):
    return permission_required(Permission.BACKEND)(func)


# 社区权限管理(仅关注后才可访问）
def social_required(user):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_joining(user):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
