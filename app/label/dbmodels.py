#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:27
# email:515337036@qq.com
# ======================

from .. import db
from datetime import datetime


# 标签系统：标签基础模型
class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 用户标签，外键关联User用户模型
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 文章标签，外键关联User用户模型
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # 短消息标签，外键关联Message用户模型
    # message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    # 私信标签，外键关联Letter用户模型
    # letter_id = db.Column(db.Integer, db.ForeignKey('letters.id'))

    # 基础标签（借助关系表，多对多关系映射）
    basics = db.relationship('BasicLabels', backref='label', lazy='dynamic')
    # 自定义标签（借助关系表，多对多关系映射）
    customs = db.relationship('CustomLabels', backref='label', lazy='dynamic')

    pass


# 标签系统：基础标签身份模型
class BasicLabelRole(db.Model):
    __tablename__ = 'basic_role'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(16))
    is_user = db.Column(db.Boolean, default=True)
    is_post = db.Column(db.Boolean, default=True)
    is_message = db.Column(db.Boolean, default=True)
    is_letter = db.Column(db.Boolean, default=True)

    # 基础标签（借助关系表，多对多关系映射）
    labels = db.relationship('BasicLabels', backref='basic', lazy='dynamic')

    # 数据库操作：插入默认基础标签数据
    @staticmethod
    def insert_roles():
        # 角色关系类别：【用户, 文章, 短消息, 私信】
        roles = {
            '基础会员': [True, True, True, True],
            'vip会员': [True, True, True, True],
            '超短选手': [True, False, False, False],
            '长线达人': [True, False, False, False],
            '韭菜萌新': [True, False, False, False],
            '炒股达人': [True, False, False, False],
            '技术面': [True, True, False, False],
            '基本面': [True, True, False, False],
            '每日时评': [False, True, True, False],
            '每日收评': [True, True, False, False],
            '系统私信': [False, False, False, True],
        }
        for r in roles:
            role = BasicLabelRole.query.filter_by(name=r).first()
            if role is None:
                role = BasicLabelRole(name=r)
            role.is_user = roles[r][0]
            role.is_post = roles[r][1]
            role.is_message = roles[r][2]
            role.is_letter = roles[r][3]
            db.session.add(role)
            db.session.commit()

    pass


# 基础标签关系表（标签——基础标签）
class BasicLabels(db.Model):
    __tablename__ = 'basic_labels'
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('basic_role.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 标签系统：自定义标签身份模型
class CustomLabelRole(db.Model):
    __tablename__ = 'custom_role'
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(16))
    is_user = db.Column(db.Boolean, default=True)
    is_post = db.Column(db.Boolean, default=True)
    is_message = db.Column(db.Boolean, default=True)
    is_letter = db.Column(db.Boolean, default=True)

    # 自定义标签（借助关系表，多对多关系映射）
    labels = db.relationship('CustomLabels', backref='custom', lazy='dynamic')

    pass


# 自定义标签关系表（标签——自定义标签）
class CustomLabels(db.Model):
    __tablename__ = 'custom_labels'
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)
    custom_id = db.Column(db.Integer, db.ForeignKey('custom_role.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

