#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/14:16:23
# email:515337036@qq.com
# ======================

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth  # flask扩展-HttpAuth模块支持HTTP认证
from ..dbmodels import User
from . import api
from .errors import unauthorized, forbidden

# HTTP认证只涉及API蓝本，故只在此初始化
auth = HTTPBasicAuth()

# api蓝本请求前检查
# 访问限制：只有认证用户可以访问这个路由
@api.before_request
@auth.login_required
def before_request():
    # 不是匿名用户或者不是已认证用户
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


# API-检查密码或密码令牌
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token.lower()).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


# API-认证错误
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


# API-特殊URL-请求获取密码令牌
@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
