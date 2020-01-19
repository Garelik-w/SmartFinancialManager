#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/9:13:29
# email:515337036@qq.com
# ======================
from flask import render_template, redirect, flash, url_for, current_app, request
from flask_login import current_user
from ..dbmodels import Permission, User, Comment
from ..decorators import admin_required, permission_required
from flask_login import login_required
from .. import db
from . import main  # 导入蓝本对象


# 社交系统-功能-审核用户评论
@main.route('/moderate')
@login_required
@permission_required(Permission.BACKEND)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


# 社交系统-功能-审核通过评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.BACKEND)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


# 社交系统-功能-审核禁止评论
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.BACKEND)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))