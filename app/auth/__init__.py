#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/2:17:40
# email:515337036@qq.com
# ======================

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views, fans


FansSource = {
    'Jrtt': '今日头条',
    'Xq': '雪球',
    'Wb': '微博',
    'Zsxq': '知识星球',
    'Qq': 'QQ等社群',
    'Wx': '微信公众号',
    'Personal': '个人渠道',
    'Others': '其他平台',
}

# 蓝本模板调用会自动插入词典参数（钩子函数）
@auth.app_context_processor
def inject_permissions():
    return dict(FansSource=FansSource)
