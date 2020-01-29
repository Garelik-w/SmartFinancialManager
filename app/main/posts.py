#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/7:15:39
# email:515337036@qq.com
# ======================

from flask import render_template, flash, redirect, url_for, request, current_app, abort, make_response
from flask_login import current_user, login_required
from ..dbmodels import Permission, Post, Comment
from .forms import CommentForm, PostForm
from .. import db
from . import main  # 导入蓝本对象

# 文章系统-文章页面
# 每个文本内容都对应一个URL链接
@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        # POST
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('您的评论已经被发布.')
        return redirect(url_for('main.post', id=post.id, page=-1))
    # GET
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['FLASK_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


# 文章系统-文章内容编辑修改
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        # 生成标签(后期需要判断是否是第一次生成，不是则修改）
        post.generate_label()
        db.session.add(post)
        db.session.commit()
        flash('文章已经成功修改！')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


# 文章系统-功能-显示所有用户的文章
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


# 文章系统-功能-仅显示关注用户的文章
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp