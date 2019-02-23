from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import requests
from lxml import etree
import matplotlib as plt
import numpy as np


def get_standard():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    standard_url = 'https://consumeprod.alipay.com/record/standard.htm'
    login_url = 'https://auth.alipay.com/login/index.htm'
    driver.get(standard_url)
    time.sleep(2)
    element = driver.find_element_by_class_name('barcode')
    driver.save_screenshot('screenshot.png')
    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']

    im = Image.open('screenshot.png')
    im = im.crop((left, top, right, bottom))
    im.save('screenshot.png')
    driver.close()
    #
    # while True:
    #     print('验证是否登录')
    #     if '我的账单' in driver.title:
    #         cookie = driver.get_cookies()
    #         print('成功获取cookies')
    #         break
    #     else:
    #         time.sleep(2)
    # for i in range(2):
    #     print(driver.page_source)
    #     time.sleep(15)
    # driver.close()
# get_standard()


def single():
    s_count, a_count = 0, 0
    all_count = []
    for i in range(1000000):
        if all_count[-9:].count(1) == 0 and len(all_count[-9:]) == 9:
            s_count += 1
            all_count.append(1)
        else:
            if random.random() >= 0.2:
                a_count += 1
                all_count.append(0)
            else:
                s_count += 1
                all_count.append(1)
    print(s_count)
    print(a_count)


def mutli():
    s_count, a_count = 0, 0
    for i in range(0, 1000000, 10):
        s_count_temp = 0
        for i in range(10):
            if s_count_temp == 0 and i == 9:
                s_count += 1
            else:
                if random.random() >= 0.2:
                    a_count += 1
                else:
                    s_count += 1
                    s_count_temp += 1
    print(s_count)
    print(a_count)


mutli()