#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/1:14:34
# email:515337036@qq.com
# ======================


import os
# flask扩展 Script命令行
from flask_script import Manager, Shell
# flask扩展 Migrate数据库迁移工具
from flask_migrate import Migrate, MigrateCommand
# 从app构造文件导入工厂函数和相关初始化实例
from app import create_app, db
from app.dbmodels import User, Role, Permission

app = create_app('development')
manager = Manager(app)  # flask-script命令行操作初始化
migrate = Migrate(app, db)  # flask-Migrate数据库迁移初始化

# shell命令调试用(flask-script)
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission)


manager.add_command('migrate', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
    # app.run()  # == python manager.py runserver
