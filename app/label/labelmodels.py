#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2020/1/12:16:27
# email:515337036@qq.com
# ======================

from app import db
from datetime import datetime


# 标签系统-标签权限
class LabelPermission:
    normal = 0
    vip = 1


# 标签系统：标签基础模型
class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 基础属性，默认是0:normal，大V有权限设置为1:vip
    permission = db.Column(db.Boolean, default=False)
    # 用户标签，外键关联User用户模型（实际调用和初始化的时候，都用反身变量user代替）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 文章标签，外键关联User用户模型（实际调用和初始化的时候，都用反身变量post代替）
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # 短消息标签，外键关联Message用户模型
    # message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    # 私信标签，外键关联Letter用户模型
    # letter_id = db.Column(db.Integer, db.ForeignKey('letters.id'))

    # 基础标签（借助关系表，多对多关系映射）
    basics = db.relationship('BasicLabelRelation', backref='label', lazy='dynamic')
    # 自定义标签（借助关系表，多对多关系映射）
    customs = db.relationship('CustomLabelRelation', backref='label', lazy='dynamic')

    # 标签初始化
    def __init__(self, **kwargs):
        super(Label, self).__init__(**kwargs)
        if self.permission is None:
            self.permission = LabelPermission.normal
        role = BasicLabelRole.query.filter_by(id=1).first()  # 基础标签1就是默认标签
        f = BasicLabelRelation(label=self, basic=role)
        f.hide = False
        db.session.add(f)

    # 创建一个基础标签关联
    # 判断这个label_id对应的基础标签是否已经存在，如果不存在则添加
    def generate_base_relation(self, basic_id=1, is_hide=True):
        if self.basics.filter(BasicLabelRelation.basic_id == basic_id).first() is None:
            role = BasicLabelRole.query.filter_by(id=basic_id).first()
            f = BasicLabelRelation(label=self, basic=role)
            # 默认隐藏标签
            f.hide = is_hide
            db.session.add(f)

    # 删除一个基础标签关联
    # 判断这个label_id对应的基础标签是否已经存在，如果存在则删除
    def delete_base_relation(self, basic_id=1):
        pass

    # 创建一个自定义标签关联
    def generate_custom_relation(self, custom_id=1, is_hide=True):
        role = CustomLabelRole.query.filter_by(id=custom_id).first()
        f = CustomLabelRelation(label=self, basic=role)
        # 默认隐藏标签
        f.hide = is_hide
        db.session.add(f)

    # def ref_basic(self, basic):
    #     if not self.is_basic_label(basic):
    #         f = BasicLabelRole(label_id=self, basic_id=basic)
    #         db.session.add(f)

    # def is_basic_label(self, label):
    #     if label.id is None:
    #         return False
    #     return self.basics.filter_by(
    #         label_id=label.id).first() is not None


# 标签系统：基础标签身份模型
class BasicLabelRole(db.Model):
    __tablename__ = 'basic_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    is_user = db.Column(db.Boolean, default=True)
    is_post = db.Column(db.Boolean, default=True)
    remarks = db.Column(db.String(64))
    color = db.Column(db.String(12))

    # 基础标签（借助关系表，多对多关系映射）
    labels = db.relationship('BasicLabelRelation', backref='basic', lazy='dynamic')

    # 数据库操作：插入默认基础标签数据
    @staticmethod
    def create_roles():
        # 角色关系类别：【用户, 文本, 备注, 标签颜色】
        roles = {
            '默认': [True, True, '默认选项', 'red'],
            '超短选手': [True, True, '投资风格偏向超短线', 'blue'],
            '长线达人': [True, True, '投资风格偏向长线', 'pink'],
            '韭菜萌新': [True, False, '对投资几乎一窍不通', 'green'],
            '炒股达人': [True, False, '对投资有独到理解', 'amber'],
            '技术面': [True, True, '倾向股票的技术面', 'cyan'],
            '基本面': [True, True, '倾向股票的基本面', 'purple'],
            '长文章': [False, True, '精品文章', 'red'],
            '短消息': [False, True, '动态消息', 'yellow'],
            '私信': [False, True, '专属私信', 'blue'],
            '大金融相关': [False, True, '证券、银行等大金融相关概念', 'blue'],
            '大科技相关': [False, True, '5G、半导体等科技相关概念', 'cyan'],
            '大制造相关': [False, True, '基建、工业4.0等制造业相关概念', 'amber'],
            '大消费相关': [False, True, '白酒、食品等消费概念', 'yellow'],
            '大健康相关': [False, True, '医药、养老等健康相关概念', 'green'],
        }
        for r in roles:
            role = BasicLabelRole.query.filter_by(name=r).first()
            if role is None:
                role = BasicLabelRole(name=r)
            role.is_user = roles[r][0]
            role.is_post = roles[r][1]
            role.remarks = roles[r][2]
            role.color = roles[r][3]
            db.session.add(role)
            db.session.commit()


# 基础标签关系表（标签——基础标签）
class BasicLabelRelation(db.Model):
    __tablename__ = 'basic_relations'
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('basic_role.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hide = db.Column(db.Boolean, default=True)  # 是否隐藏，默认为true
    # view = db.Column(db.Boolean, default=False)


# 标签系统：自定义标签身份模型
class CustomLabelRole(db.Model):
    __tablename__ = 'custom_role'
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(16))
    is_user = db.Column(db.Boolean, default=True)
    is_post = db.Column(db.Boolean, default=True)
    remarks = db.Column(db.String(64))
    color = db.Column(db.String(12))

    # 自定义标签（借助关系表，多对多关系映射）
    labels = db.relationship('CustomLabelRelation', backref='custom', lazy='dynamic')

    pass


# 自定义标签关系表（标签——自定义标签）
class CustomLabelRelation(db.Model):
    __tablename__ = 'custom_relations'
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)
    custom_id = db.Column(db.Integer, db.ForeignKey('custom_role.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hide = db.Column(db.Boolean, default=True)  # 是否隐藏，默认为true
    # view = db.Column(db.Boolean, default=False)

