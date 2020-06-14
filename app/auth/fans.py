#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/13:21:21
# email:515337036@qq.com
# ======================

from flask import render_template, url_for, flash, current_app, redirect, request
from flask_login import login_required, current_user
from ..dbmodels import User, Permission, Follow, Analysis
from ..label.labelmodels import BasicLabelRelation, CustomLabelRelation, BasicLabelRole, CustomLabelRole
from . import auth
from .. import db
from ..decorators import permission_required
from datetime import datetime

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
    return render_template('auth/followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

# ------------------------------------------------ 后台-粉丝后勤助理模块 ------------------------------------------------
# 粉丝后勤助理模块-粉丝概览
@auth.route('/fans/<username>')
# @permission_required(Permission.LABEL)
def fans_overview(username):
    user = User.query.filter_by(username=username).first()
    myfans = user.fans  # 获取用户的粉丝过滤器
    mydatas = user.analysis.order_by(Analysis.timestamp.desc())  # 获取用户的数据过滤器（已按照时间顺序由最新的开始排序）
    datas_30 = mydatas.all()[0:30]  # 获取近30日的数据

    # ---- 粉丝总数计算 ---- #
    fans_total_new = myfans.count()  # 获取最新的粉丝总人数
    fans_total_last = int(mydatas.first().fans_total)  # 昨日登录的粉丝总人数
    fans_net_change = abs(fans_total_new - fans_total_last) / fans_total_last if fans_total_last is not 0 else 0
    # ---- 新增粉丝数计算 ---- #
    myfans_added = myfans.filter(Follow.timestamp > mydatas.first().timestamp)  # 找出今日关注大V的粉丝（就是新增粉丝）
    fans_added = myfans_added.count()  # 获取今日新增粉丝数（不是净值）
    fans_added_last = int(mydatas.first().fans_added)  # 昨日的新增粉丝数（不是净值）
    fans_added_change = abs(fans_added - fans_added_last) / fans_added_last if fans_added_last is not 0 else 0
    # ---- 新减粉丝数计算 ---- #
    fans_reduce = fans_total_new - fans_total_last - fans_added  # 获取今日新减粉丝数（不是净值）
    fans_reduce_last = int(mydatas.first().fans_reduce)  # 昨日的新减粉丝数（不是净值）
    fans_reduce_change = abs(fans_reduce - fans_reduce_last) / fans_reduce_last if fans_reduce_last is not 0 else 0
    # ---- 粉丝来源计算 ---- #
    fans_source = [User.query.filter_by(id=fans.fans_id).first().source for fans in myfans]
    from_wb = fans_source.count('Wb')
    from_jrtt = fans_source.count('Jrtt')
    from_xq = fans_source.count('Xq')
    from_wx = fans_source.count('Wx')
    from_qq = fans_source.count('Qq')
    from_others = fans_source.count('Others') + fans_source.count('Zsxq') + fans_source.count('Personal')
    source = {'wb': from_wb, 'jrtt': from_jrtt, 'xq': from_xq, 'wx': from_wx, 'qq': from_qq, 'others': from_others}
    source_last = [int(datas_30[0].source_wb), int(datas_30[0].source_jrtt), int(datas_30[0].source_xq), int(datas_30[0].source_wx),
                   int(datas_30[0].source_qq), int(datas_30[0].source_others)]

    # ---- 获取粉丝的用户信息（前端负责分页） ---- #
    fans_infos = [User.query.filter_by(id=fans.fans_id).first() for fans in myfans]

    # ---- 数据库的基础标签和自定义标签（根据栏目取对应的）全部项目 ---- #
    basic_roles = [role for role in BasicLabelRole.query.filter_by(is_user=True).all()]
    custom_roles = [role for role in CustomLabelRole.query.filter_by(is_user=True).all()]
    # 计算序列标签的对应序列（因为数据库id从1开始，所以这里手动-1）
    basic_index = [role.id-1 for role in basic_roles]
    custom_index = [role.id-1 for role in custom_roles]
    # 转换为字典类型
    basic_label_roles = {'name': [basic_role.name for basic_role in basic_roles],
                         'remarks': [basic_role.remarks for basic_role in basic_roles],
                         'color': [basic_role.color for basic_role in basic_roles]}
    custom_label_roles = {'name': [custom_role.name for custom_role in custom_roles],
                          'remarks': [custom_role.remarks for custom_role in custom_roles],
                          'color': [custom_role.color for custom_role in custom_roles]}

    # ---- 获取每个粉丝对应的choice标签和free标签信息（序列） ---- #
    basic_choice_labels, basic_free_labels, basic_choice_view, basic_choice_limit = [], [], [], []
    custom_choice_labels, custom_free_labels, custom_choice_view, custom_choice_limit = [], [], [], []
    fans_label_ids = []
    basic_label_lists, custom_label_lists = [], []
    for fans_info in fans_infos:
        fans_label = fans_info.labels.filter_by(idol_id=user.id).first()  # 找到粉丝关联这个大V社区的唯一标签
        if fans_label is None:
            fans_info.insert_basic_label(idol_id=user.id)
            db.session.commit()
        # 获取用户标签对应的序号-基础标签
        basic_choice = [basic_label.basic_id-1 for basic_label in
                        BasicLabelRelation.query.filter_by(label_id=fans_label.id).all()]
        basic_choice_labels.append(basic_choice)
        basic_free_labels.append([i for i in basic_index if i not in basic_choice])
        # 获取用户标签对应的序号-自定义标签
        custom_choice = [custom_label.custom_id - 1 for custom_label in
                         CustomLabelRelation.query.filter_by(label_id=fans_label.id).all()]
        custom_choice_labels.append(custom_choice)
        custom_free_labels.append([i for i in custom_index if i not in custom_choice])

        # 获取已选择标签的view和limit属性-基础标签
        basic_choice_view.append(
            [int(basic_label.view) for basic_label in BasicLabelRelation.query.filter_by(label_id=fans_label.id).all()])
        basic_choice_limit.append(
            [int(basic_label.limit) for basic_label in BasicLabelRelation.query.filter_by(label_id=fans_label.id).all()])
        # 获取已选择标签的view和limit属性-自定义标签
        custom_choice_view.append(
            [int(custom_label.view) for custom_label in CustomLabelRelation.query.filter_by(label_id=fans_label.id).all()])
        custom_choice_limit.append(
            [int(custom_label.limit) for custom_label in CustomLabelRelation.query.filter_by(label_id=fans_label.id).all()])
        # 把每个粉丝对应的唯一label_id传到前端用以返回相应的数据
        fans_label_ids.append(fans_label.id)
        # 记住每个粉丝的属性序列，用以在前端调用
        basic_label_lists.append(list(range(len(basic_choice))))
        custom_label_lists.append(list(range(len(custom_choice))))
    # 前端只能依赖字典的遍历来对应用户和id
    fans_len = list(range(len(fans_infos)))
    fans_info_dicts = {i: fans_infos[i] for i in fans_len}
    # 把标签的信息封装在一起（同维的）
    basic_label_relations = {'choice': basic_choice_labels, 'free': basic_free_labels, 'view': basic_choice_view,
                             'limit': basic_choice_limit, 'index': basic_label_lists}
    custom_label_relations = {'choice': custom_choice_labels, 'free': custom_free_labels, 'view': custom_choice_view,
                              'limit': custom_choice_limit, 'index': custom_label_lists}

    return render_template('social-fans.html', fans_total_new=fans_total_new, fans_total_last=fans_total_last,
                           datas_30=datas_30, fans_added=fans_added, fans_added_last=fans_added_last,
                           fans_added_change=round(fans_added_change*100, 2), fans_reduce=fans_reduce,
                           fans_reduce_last=fans_reduce_last, fans_net_change=round(fans_net_change*100, 2),
                           fans_reduce_change=round(fans_reduce_change*100, 2), source=source, source_last=source_last,
                           fans_info_dicts=fans_info_dicts, basic_label_roles=basic_label_roles,
                           custom_label_roles=custom_label_roles, basic_label_relations=basic_label_relations,
                           custom_label_relations=custom_label_relations, fans_label_ids=fans_label_ids)
    # if user is None:
    #     flash('不存在的用户.')
    #     return redirect(url_for('main.home'))
    # page = request.args.get('page', 1, type=int)
    # pagination = user.fans.paginate(
    #     page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
    #     error_out=False)
    # follows = [{'user': item.fans, 'timestamp': item.timestamp}
    #            for item in pagination.items]
    # return render_template('auth/followers.html', user=user, title="Followers of",
    #                        endpoint='auth.followers', pagination=pagination,
    #                        follows=follows)
