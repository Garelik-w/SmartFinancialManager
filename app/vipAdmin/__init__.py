#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/29:19:52
# email:515337036@qq.com
# ======================


from flask import Blueprint

vipAdmin = Blueprint('vipAdmin', __name__)

from . import views