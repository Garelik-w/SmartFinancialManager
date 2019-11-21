#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/1:14:34
# email:515337036@qq.com
# ======================

import os
import sys
import click  # flask集成click-命令行工具
# 测试系统-导入coverage实现单元测试
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


# flask扩展 Migrate数据库迁移工具
from flask_migrate import Migrate, upgrade
# 从app构造文件导入工厂函数和相关初始化实例
from app import create_app, db
from app.dbmodels import User, Role, Follow, Permission, Post, Comment
# flask扩展 Script命令行工具
from flask_script import Manager, Shell

app = create_app('development')
migrate = Migrate(app, db)  # flask-Migrate数据库迁移初始化

# flask-click：支持命令行上下文对象
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Follow=Follow, Permission=Permission, Post=Post, Comment=Comment)


# flask-click：增加test测试命令
# 测试系统-执行单元测试并输出测试报告
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


# flask-click：增加profile命令
# 测试系统-源码分析器分析代码耗时
# 在click命令行模式下，无法执行代码里的app.run,所以需要用到flask-script命令行扩展
@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile_dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


# 部署流出-自动更新数据库表并创建角色表
@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    # User.add_self_follows()  # 我的系统没有关注自己的这个操作


# flask-script增加命令（暂不是用flask-script）
manager = Manager(app)  # flask-script命令行操作初始化
# manager.add_command('migrate', MigrateCommand)
# manager.add_command("shell", Shell(make_context=make_shell_context))

# flask-script：增加script_profile命令
# 测试系统-源码分析器（补充click命令行）
# python manager.py script_profile启动即可
@manager.command
def script_profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


# 在click命令行模式下，不需要这种方式启动。为了使用flask-script的profile命令才加上
if __name__ == '__main__':
    manager.run()
