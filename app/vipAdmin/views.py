#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/29:19:54
# email:515337036@qq.com
# ======================


from flask import render_template, redirect
from . import vipAdmin
from ..dbmodels import User

# VIP管理员控制终端页面
@vipAdmin.route('/user/<username>')
def vipuser(username):
    user = User.query.filter_by(username=username).first_or_404()
    return 'Hello, %s' % username
