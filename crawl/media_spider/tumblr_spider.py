# -*- coding: UTF-8 -*-
import sys, re, time, requests
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadingPool
sys.path.append('c:/test_py/tool')
from Mongo_pro import Mongo
from get_html import HtmlPro
class TumblrSpider:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.TumblrDb
        self.collection = self.db.Datas

        self.proxies = {'http':'http://192.168.2.100:8081'}

    def main_spider(self, url):
        html = hp.get_html(url, self.proxies)
        img_list = self.get_img(html)
        # img_list = self.deal_img(img_list)
        return html
    def get_img(self, html):
        img_list = re.findall(r'"(http://g.*?\.jpg)"', html)
        return img_list

    def deal_img(self, img_list):
        deal_img_list = []
        for img in img_list:
            if img.find('tumblr_') > 0:
                deal_img_list.append(img)
        return deal_img_list

    def ip_test(self, i):
        proxies = {'http':'http://45.78.46.129:duankou'}
        proxies['http'] = proxies['http'].replace('duankou', str(i))
        try:
            print (requests.get('http://www.tumblr.com', proxies=proxies, timeout=10).content)
            print (str(i) + '可用')
            exit()
        except Exception:
            print (str(i) + '失败')
    def mump_(self):
        m = range(594, 10000)
        pool = ThreadingPool(4)
        pool.map(self.ip_test, m)
        pool.close()
        pool.join()
    # def get_video(self, html):
if __name__ == '__main__':
    mon = Mongo()
    hp = HtmlPro()
    tum = TumblrSpider()
    # tum.mump_()
    print (requests.get('http://www.tumblr.com', proxies={'http':'http://kr4.sgateway.link:21289'}).content)