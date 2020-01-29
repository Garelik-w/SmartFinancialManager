#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/18:15:12
# email:515337036@qq.com
# ======================

import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db
from app.dbmodels import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Chrome

        # options = webdriver.ChromeOptions()  # 设置代理
        # options.add_argument('headless')

        # options.add_argument("--proxy-server=http://127.0.0.1:5000/")  # 这个应该没用
        try:
            # cls.client = webdriver.Chrome(chrome_options=options)
            chromedriverpath = r'C:\Users\wugl\PythonPrj\SmartFinancialManager-webapp\tests\chromedriver_win32\chromedriver.exe'
            # cls.client = webdriver.Chrome(chrome_options=options, executable_path=chromedriverpath)
            cls.client = webdriver.Chrome(executable_path=chromedriverpath)
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            User.generate_fake_users(20)
            Post.generate_fake_posts(20)

            # add an administrator user
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(email='john@example.com',
                         username='john', password='cat',
                         role_id=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            cls.server_thread = threading.Thread(target=cls.app.run,
                                                 kwargs={'debug': False})
            cls.server_thread.start()

            # give the server a second to ensure it is up
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # navigate to home page
        self.client.get('http://localhost:5000/')
        # time.sleep(10)
        # print('\n' + '===============' + self.client.page_source + '\n')
        self.assertTrue(re.search('Hello,\s+Stranger!',
                                  self.client.page_source))

        # navigate to login page
        self.client.find_element_by_link_text('Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)

        # login
        self.client.find_element_by_name('email'). \
            send_keys('john@example.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

        # navigate to the user's profile page
        self.client.find_element_by_link_text('Profile').click()
        self.assertIn('<h1>john</h1>', self.client.page_source)
