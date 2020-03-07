#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:21
# email:515337036@qq.com
# ======================


from flask import render_template, redirect, url_for
from . import label
from .labelmodels import Label
from .forms import LabelPermissionForm
from .. import db


@label.route('center/<label_id>')
def label_center(label_id):
    label = Label.query.filter_by(id=label_id).first_or_404()
    if label is None:
        return redirect(url_for('auth.user'))
    return render_template('label/label_center.html',
                           endpoint='auth.followers', pagination=pagination,
                           follows=follows)


@label.route('edit_permission/<label_id>')
def edit_label_permission(label_id):
    label = Label.query.filter_by(id=label_id).first_or_404()
    form = LabelPermissionForm()
    if form.validate_on_submit():
        # POST
        label.permission = form.is_vip.data
        db.session.add(label)
        db.session.commit()
    # GET
    return render_template('label/edit_permission.html', form=form)

# # 从前端获取标签id和对应的基础标签id、自定义标签id
# @label.route('insert_labels/<label_id, basic_id, custom_id, is_hide>')
# def insert_labels(label_id, basic_id, custom_id, is_hide=True):
#     label = Label.query.filter_by(id=label_id).first_or_404()
#     label.generate_base_relation(basic_id, is_hide) if basic_id is not None else 1
#     db.session.add(label)
#     db.session.commit()
