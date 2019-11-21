#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:17:40
# email:515337036@qq.com
# ======================

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
