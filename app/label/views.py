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


    return render_template('label_center.html',
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
    return render_template('edit_permission.html', form=form)