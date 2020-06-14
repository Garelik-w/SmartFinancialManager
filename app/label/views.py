#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:21
# email:515337036@qq.com
# ======================


from flask import render_template, redirect, url_for, jsonify, request
from . import label
from .labelmodels import Label, BasicLabelRelation, BasicLabelRole, CustomLabelRole, CustomLabelRelation
from .forms import LabelPermissionForm
from .. import db


@label.route('center/<label_id>')
def label_center(label_id):
    pass
    # label = Label.query.filter_by(id=label_id).first_or_404()
    # if label is None:
    #     return redirect(url_for('auth.user'))
    # return render_template('label/label_center.html',
    #                        endpoint='auth.followers')


@label.route('edit_permission/<label_id>')
def edit_label_permission(label_id):
    pass
    # label = Label.query.filter_by(id=label_id).first_or_404()
    # form = LabelPermissionForm()
    # if form.validate_on_submit():
    #     # POST
    #     label.permission = form.is_vip.data
    #     db.session.add(label)
    #     db.session.commit()
    # # GET
    # return render_template('label/edit_permission.html', form=form)

# 从前端获取标签关系表保存到数据库
@label.route('save_label_relations/<label_id>', methods=['POST'])
def save_label_relations(label_id):
    recv_data = request.get_json()
    # print(recv_data)
    # 获得该粉丝的社区唯一标签
    fans_label = Label.query.filter_by(id=label_id).first()

    # ------------ 提取新的标签数据（先不安view和limit分类，等增删完毕后再来修改view、limit属性即可） ------------ #
    view_done = recv_data['view_done']
    limit_done = recv_data['limit_done']
    # 获得新的基础标签和自定义标签的序列
    basic_choice_new = view_done[0] + limit_done[0]
    custom_choice_new = view_done[1] + limit_done[1]
    basic_choice_new = [i+1 for i in list(map(int, basic_choice_new))]  # 将字符格式的元素转为数字, 并自加1用以遍历数据库
    custom_choice_new = [i+1 for i in list(map(int, custom_choice_new))]
    # 记录好需要设置view属性和Limit属性的标签
    view_index_basic = [i+1 for i in list(map(int, view_done[0]))]
    view_index_custom = [i+1 for i in list(map(int, view_done[1]))]
    limit_index_basic = [i+1 for i in list(map(int, limit_done[0]))]
    limit_index_custom = [i+1 for i in list(map(int, limit_done[1]))]

    # ------------ 数据库的基础标签和自定义标签（根据栏目取对应的）全部项目 ------------ #
    basic_choice = [basic_label.basic_id for basic_label in
                    BasicLabelRelation.query.filter_by(label_id=label_id).all()]
    custom_choice = [custom_label.custom_id for custom_label in
                     CustomLabelRelation.query.filter_by(label_id=label_id).all()]

    # ------------ 计算标签变化并对数据库做新增和删减 ------------ #
    # 对基础标签做新增和删减（删除全部旧标签关系，再生成新的）
    # add_basic_labels = [i+1 for i in basic_choice_new if i not in basic_choice]
    # delete_basic_labels = [i+1 for i in basic_choice if i not in basic_choice_new]
    [fans_label.delete_basic_relation(basic_id=f) for f in basic_choice]  # 遍历删除这些标签关系
    # 遍历新增这些新的标签（同时修改view和limit属性）
    for role_id in basic_choice_new:
        if role_id in view_index_basic:
            fans_label.generate_basic_relation(basic_id=role_id, is_view=True, is_limit=False)
        if role_id in limit_index_basic:
            fans_label.generate_basic_relation(basic_id=role_id, is_view=False, is_limit=True)
    db.session.commit()
    # 对自定义标签做新增和删减（同时设置好view、limit属性）
    # add_custom_labels = [i+1 for i in custom_choice_new if i not in custom_choice]
    # delete_custom_labels = [i + 1 for i in custom_choice if i not in custom_choice_new]
    [fans_label.delete_custom_relation(custom_id=f) for f in custom_choice]  # 遍历删除这些标签关系
    # 遍历新增这些新的标签
    for role_id in custom_choice_new:
        if role_id in view_index_custom:
            fans_label.generate_custom_relation(custom_id=role_id, is_view=True, is_limit=False)
        if role_id in limit_index_custom:
            fans_label.generate_custom_relation(custom_id=role_id, is_view=False, is_limit=True)
    db.session.commit()

    # ------------ 把新输入的标签信息保存到数据库（name-remarks-color) ------------ #
    # 同时修改对应标签的view和limit属性
    [fans_label.create_custom_label(info['name'], info['color'], '',
                                    is_view=True, is_limit=False, is_user=True, is_text=False) for info in view_done[2]]
    [fans_label.create_custom_label(info['name'], info['color'], '',
                                    is_view=False, is_limit=True, is_user=True, is_text=False) for info in limit_done[2]]
    db.session.commit()

    # 看情况需不需要判断前面的数据库操作是否正常返回结果
    ret = {'id': label_id, 'error': True}
    return jsonify(ret)

