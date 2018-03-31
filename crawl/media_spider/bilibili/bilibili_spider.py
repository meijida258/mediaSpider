# -*- coding: UTF-8 -*-
import requests, time, random, re, json, datetime
from lxml import etree
from multiprocessing.dummy import Pool as ThreadingPool
from pymongo import MongoClient

class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.bili_db = self.client.Bilibili
        self.bili_collection = self.bili_db.Video

        self.ip_db = self.client.Proxy
        self.ip_collection = self.ip_db.Ip


    def insertMessage(self, video_dict):
        if mon.bili_collection.find({'video_link':video_dict['video_link']}).count() == 0:
            mon.bili_collection.insert(video_dict)
            print '录入1条message'
        else:
            print '重复消息'

    def get_proxy_list(self):
        proxy_list = []
        for ip_dict in self.ip_collection.find({'canVisit': 'bilibili'}):
            http_dict = {'http':'http://%s' % ip_dict['proxy']}
            proxy_list.append(http_dict)
        proxy_list.append(None)
        return proxy_list

class Bilibili():
    def __init__(self):
        self.headers = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)']

        self.baseUrl = 'http://api.bilibili.com/archive_rank/getarchiverankbypartion?callback=jQuery172038457941875197976_timestamp&type=jsonp&tid=tid_number&pn=page_number' # timestamp:时间戳，tid:tid，pn:页数
        self.videoTid = '34'
        self.start_page, self.end_page = 1, 280
        self.proxy_list = mon.get_proxy_list()

    def get_html(self, url):
        while True:
            time.sleep(random.uniform(3, 5))
            proxy = self.proxy_list[random.randint(0,  len(self.proxy_list) - 1)]
            try:
                html = requests.get(url, proxies=proxy, timeout=30,)
                return html
            except Exception:
                print '使用%s获取%s出错' % (str(proxy),url)


    def get_video(self, url):
        print '正在获取第%s页' %(url.split('=')[-1])
        while True:
            html = self.get_html(url).content
            if html.find('jQuery') >= 0:
                break
        value = json.loads(html[42:-2])
        for each_video in  value['data']['archives']:
            video_dict = {}
            video_dict['video_link'] = 'http://www.bilibili.com/video/av' + str(each_video['aid']) + '/'
            video_dict['author'] = each_video['author']
            video_dict['copyright'] = each_video['copyright']
            video_dict['create'] = each_video['create']
            video_dict['description'] = each_video['description']
            video_dict['play'] = each_video['play']
            tag_all = ''
            for tag in each_video['tags']:
                tag_all += tag + ','
            video_dict['tags'] = tag_all
            video_dict['title'] = each_video['title']
            video_dict['typename'] = each_video['tname']
            video_dict['video_review'] = each_video['video_review']
            video_dict['tid'] = each_video['tid']
            mon.insertMessage(video_dict)

    def get_all_page_url(self, start_page, end_page):
        page_url_list = []
        for page in range(start_page, end_page):
            url = self.baseUrl
            timestamp = str(int(time.mktime(datetime.datetime.now().timetuple()))) + str(random.randint(900, 999))
            url = url.replace('timestamp', timestamp)
            url = url.replace('tid_number', self.videoTid)
            url = url.replace('page_number', str(page))
            page_url_list.append(url)
        return page_url_list

    def main(self):
        page_url_list = self.get_all_page_url(self.start_page, self.end_page)
        # for url in page_url_list:
        #     self.get_video(url)
        pool = ThreadingPool(4)
        pool.map(self.get_video, page_url_list)
        pool.close()
        pool.join()
if __name__ == '__main__':
    mon = Mongo()
    bili = Bilibili()
    bili.main()
