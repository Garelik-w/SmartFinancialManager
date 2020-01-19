#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:21
# email:515337036@qq.com
# ======================


from flask import render_template
from . import label
from .. import db


@label.route('label_test')
def label_test():
    render_template('测试一下')