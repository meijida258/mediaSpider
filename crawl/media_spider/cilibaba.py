# -*- coding: UTF-8 -*-
import re, requests, random, time, json
from pymongo import MongoClient
from lxml import etree
class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.movie_db = self.client.MovieCili
        self.movie_collection = self.movie_db.Cili

    def insert_cili_address(self, cili_dict):
        if self.movie_collection.find({'cili_hashes':cili_dict['cili_name']}).count() == 0:
            self.movie_collection.insert(cili_dict)
class Cili():
    def __init__(self):
        self.search_url = 'http://www.cilibaba.com/'
        self.user_agent = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)']

    def get_html(self, url):
        while True:
            try:
                html = requests.get(url, headers={'User-Agent':self.user_agent[random.randint(0, len(self.user_agent) - 1)]},
                                        timeout=45)
                return html
            except Exception:
                print ('获取url失败，重新获取')

    def get_search_result(self, keyword):
        target_url = self.search_url + 'search/' + keyword
        while True:
            html = self.get_html(target_url).text
            title = re.findall(r'<title>(.*?)</title>', html)[0]
            if title.encode('utf-8').find(keyword) >= 0:
                break
        selector = etree.HTML(html)
        results = selector.xpath('//*[@class="x-item"]')
        if len(results) != 0:
            for result in results[:1]:
                cili_name = result.xpath('div[1]/a/@title')[0]
                cili_info = result.xpath('div[3]/text()')[0]
                cili_size = re.findall(r'size: (.*?)  To', cili_info)[0]
                cili_hashes = result.xpath('div[1]/a/@href')[0].split('/')[-1]
                cili_dict = {}
                cili_dict['cili_name'] = cili_name
                cili_dict['cili_size'] = cili_size
                cili_dict['cili_hashes'] = cili_hashes
                self.get_cili_address(cili_dict)
        else:
            cili_dict = {}
            cili_dict['cili_name'] = keyword
            cili_dict['cili_link'] = '没找到'
            mon.insert_cili_address(cili_dict)
    def get_cili_address(self, cili_dict):
        while True:
            html = self.get_html('http://www.cilibaba.com/api/json_info?hashes=' + cili_dict['cili_hashes']).content
            if html.find(cili_dict['cili_hashes']) >= 0:
                break
        value = json.loads(html)
        cili_dict['cili_link'] = 'magnet:?xt=urn:btih:' + value['result'][0]['info_hash'] + '&dn=name:' \
                                 + cili_dict['cili_name'] + '|size:' + cili_dict['cili_size']
        mon.insert_cili_address(cili_dict)
if __name__ == '__main__':
    cl = Cili()
    mon = Mongo()
    #a = mon.movie_collection.find()
    #b = open('a.txt','a')
    #for i in a:
    #    if i['cili_link'] != u'没找到':
    #        b.write(i['cili_link'].encode('utf-8'))
    #        b.write('\n')
    #b.close()
