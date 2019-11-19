#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================
# author:GarryLin-w
# time: 2019/11/18:17:03
# email:515337036@qq.com
# ======================

from selenium import webdriver
import time
import re

chrome_driver_path = r'C:\Users\wugl\PythonPrj\SmartFinancialManager-webapp\tests\chromedriver_win32\chromedriver.exe'
driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get('http://localhost:5000/')
time.sleep(10)
page1 = driver.page_source
if re.search('Hello,\s+Stranger!', page1):
    print('yes')
else:
    print('no')
driver.close()
