import sys
sys.path.append('..')
from tool.ProxyMantenance import MongoPro, ProxyUse
from tool.GetHtml import HtmlPro
from pymongo import MongoClient
import time, asyncio, queue
from lxml import etree
from multiprocessing.dummy import Pool

client = MongoClient('localhost', 27017)
photo_db = client.QQ
photo_collection = photo_db.Photo
url_collection = photo_db.Url

hp = HtmlPro()
mp = MongoPro()
pu = ProxyUse()


def get_page_list():
    start_url = 'http://www.woyaogexing.com/touxiang/weixin/index.html'
    result = [start_url]
    for i in range(2, 7):
        result.append(start_url.replace('index', 'index_%s' %str(i)))
    return result

def get_imgs_url(url):
    print('获取%s' % url)
    if url_collection.find({'source_page':url}).count() > 20:
        return

    proxy = pu.get_random_proxy('http')
    while True:
        page_content = hp.get_html(url, proxies=proxy)
        if page_content:
            break
        else:
            proxy = pu.get_random_proxy('http')

    html = etree.HTML(page_content.text)
    for i in html.xpath('//*[@class="txList "]/a[1]/@href'):
        total_url = 'http://www.woyaogexing.com/' + i
        if url_collection.find({'url':total_url}).count() == 0:
            url_collection.insert({'url':total_url, 'source_page':url})
    print('获取%s完成' %url)


def pool_():
    url_list = get_page_list()
    pool = Pool(4)
    pool.map(get_imgs_url, url_list)
    pool.close()
    pool.join()

# pool_()

def get_img(url_dict):
    url = url_dict['url']
    print('获取%s' %url)
    if photo_collection.find({'source_url':url}).count() > 15:
        print('%s已完成获取' % url)
        return

    proxy = pu.get_random_proxy('http')
    while True:
        page_html = hp.get_html(url, proxies=proxy)
        if page_html:
            break
        else:
            proxy = pu.get_random_proxy('http')
    print('页面获取完成')

    html = etree.HTML(page_html.text)
    img_list = html.xpath('//*[@class="lazy"]/@src')
    print('获得图片%s张' %str(len(img_list)))

    count = 0
    for img in html.xpath('//*[@class="lazy"]/@src'):
        if photo_collection.find({'img':img}).count() == 0:
            photo_collection.insert({'img':img, 'source_url':url, 'content':'fengjing'})
            count += 1
    print('有效图片%s张' %str(count))

def pool2():
    img_urls_list = url_collection.find()[145:240]

    pool = Pool(8)
    pool.map(get_img, img_urls_list)
    pool.close()
    pool.join()

# pool2()

import json

def get_img_list_f():
    boy_imgs = img_filter(photo_collection.find({"content":'boy'}))[:1500]
    girl_imgs = img_filter(photo_collection.find({"content":'girl'}))[:1500]
    katong_imgs = img_filter(photo_collection.find({'content':'katong'}))[:1500]
    fj_imgs = img_filter(photo_collection.find({"content":'fengjing'}))

    pic_set = boy_imgs + girl_imgs + katong_imgs + fj_imgs
    sorted(pic_set)
    print(len(pic_set))
    a = json.dumps(pic_set)
    with open('C:/Users/Administrator/Desktop/nan.txt', 'w') as fl:
        fl.write(a)
    fl.close()

def img_filter(mongo_list):
    result = []
    for i in mongo_list:
        if result.count(i['img']) == 0 and i['img'].find('400x400') > 0:
            result.append(i['img'])
    return result

get_img_list_f()
