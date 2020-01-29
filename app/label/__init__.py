#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:20
# email:515337036@qq.com
# ======================


from flask import Blueprint

label = Blueprint('label', __name__)

from . import views, labelmodels
