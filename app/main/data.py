#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/2/20:21:24
# email:515337036@qq.com
# ======================

from flask import url_for
from datetime import datetime, timedelta
from ..dbmodels import User, Analysis
from .. import db, scheduler
from flask_login import login_required, current_user
from . import main  # 导入蓝本对象


def update_database():
    print("数据更新发任务执行中，当前时间为:%s" % (datetime.now()))
    # 载入flask向下文对象
    with scheduler.app.app_context():
        # 遍历所有用户，只对大V进行数据更新
        for user in User.query.all():
            if user.is_supervipadmin():
                # 判断存储的最早数据是否超过30天，如果超过则删掉（不强求数据一定是30，只是确保动态平衡）
                del_data = user.analysis.first()
                if del_data.timestamp < (datetime.utcnow() - timedelta(days=30)):
                    db.session.delete(del_data)
                    db.session.commit()
                # 更新最新一天的数据
                Analysis.append_analysis_data(user.id)
                db.session.commit()
        print("更新完毕")

