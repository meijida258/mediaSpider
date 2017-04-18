# -*- coding: UTF-8 -*-
import requests, os, random
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool
class DownLoad():
    def __init__(self):
        self.proxyDicts = mon.collection.find()
        self.proxyList = []
        for proxyDict in self.proxyDicts:
            self.proxyList.append(proxyDict['proxy'])

    def loadContent(self, url):
        proxies = {}
        proxies['http'] = 'http://%s' % self.proxyList[random.randint(0, len(self.proxyList) - 1)]
        try:
            html = requests.get(url,proxies=proxies,timeout=60).content
        except Exception:
            html = requests.get(url).content
        return html

    def main(self, urls, savePlace):
        self.savePlace = savePlace
        if type(urls) == list:
            pool = ThreadPool(4)
            pool.map(self.mainPro, urls)
            pool.close()
            pool.join()
        else:
            self.mainPro(urls)

    def mainPro(self,url):
        url = url.encode('utf-8')
        html = self.loadContent(url)
        itemType = url.split('.')[-1]
        self.saveDownLoad(html, itemType)

    def saveDownLoad(self, html, itemType):
        if not os.path.exists(self.savePlace):
            os.mkdir(self.savePlace)
        itemCount = os.listdir(self.savePlace)
        saveNameTotal = str(len(itemCount) + 1) + '.' + itemType
        savePlaceTotal = self.savePlace + '/' + saveNameTotal
        with open(savePlaceTotal, 'wb') as fl:
            fl.write(html)
        fl.close()
        print ('保存成功')

class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Proxy
        self.collection = self.db.Ip

if __name__ == '__main__':
    mon = Mongo()
    down = DownLoad()
else:
    mon = Mongo()
    down = DownLoad()
