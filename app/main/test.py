#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/19:19:47
# email:515337036@qq.com
# ======================

from flask_sqlalchemy import get_debug_queries
from flask import current_app, abort, request
from . import main

# 测试系统-查询超时记录
# 在main脚本路由请求结束后执行
@main.after_app_request
def after_request(response):
    # get_debug_queries 获取当前路由请求的所有查询元素
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


# 测试系统-关闭web服务器
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'