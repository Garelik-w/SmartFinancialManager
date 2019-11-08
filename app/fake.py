#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/7:21:18
# email:515337036@qq.com
# ======================


from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .dbmodels import User, Post


# 生成假用户信息（在数据库模型中调用）
def generate_fake_users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


# 生成假文章信息（在数据库模型中调用）
def generate_fake_posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
