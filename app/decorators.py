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
from .dbmodels import Permission, User


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


# 这个装饰器不需要外部参数，直接处理函数本身的参数。？？ 装饰器由问题，暂时不搞。
# 社区权限管理(仅关注后才可访问）
# def social_required(current_user):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             social_list = current_user.followed.filter_by().followed_id
#             # social_admin = User.query.filter_by(id=social_admin_id).first_or_404()
#             # if not current_user.is_following(username):
#             #     abort(403)
#             if social_list is None:
#                 return "您还没加入社区，请关注大V加入社区"
#             kwargs['socials'] = social_list
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator
