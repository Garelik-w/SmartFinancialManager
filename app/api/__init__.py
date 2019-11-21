#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/14:16:21
# email:515337036@qq.com
# ======================

from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, posts, users, comments, errors
