#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/13:21:21
# email:515337036@qq.com
# ======================

from flask import render_template, url_for, flash, current_app, redirect, request
from flask_login import login_required, current_user
from ..dbmodels import User, Permission
from . import auth
from .. import db
from ..decorators import permission_required

# ------------------------------------ 用户系统-关注模块 ------------------------------------ #
# 社交系统-功能-关注指定用户
@auth.route('/follow/<username>')
@login_required
@permission_required(Permission.BASIC)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户！')
        return redirect(url_for('.home'))
    if current_user.is_following(user):
        flash('您已经关注此用户.')
        return redirect(url_for('auth.user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('您已成功关注 %s.' % username)
    return redirect(url_for('auth.user_profile', username=username))


# 社交系统-功能-取消关注指定用户
@auth.route('/unfollow/<username>')
@login_required
@permission_required(Permission.BASIC)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('main.home'))
    if not current_user.is_following(user):
        flash('您已经取消关注此用户！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('您已成功取消关注 %s ！' % username)
    return redirect(url_for('auth.user_profile', username=username))


# 社交系统-查看粉丝的页面
@auth.route('/fans/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    pagination = user.fans.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.fans, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='auth.followers', pagination=pagination,
                           follows=follows)


# 社交系统-查看关注的人的页面
@auth.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户.')
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)
