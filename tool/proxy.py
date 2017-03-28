# -*- coding: UTF-8 -*-
import time,requests, random, re, datetime
from lxml import etree
from multiprocessing.dummy import Pool as ThreadPool
from pymongo import MongoClient
from fake_useragent import UserAgent

class Tool():
    def __init__(self):

        self.weibo_cookie = []

    def getHtml(self, url, cookie=None,proxies=None):
        failed_count = 0
        while failed_count < 2:
            try:
                time.sleep(random.uniform(1, 2))
                html = requests.get(url, cookies=cookie, timeout=15, proxies=proxies, headers={'User-Agent':str(ua.random)}).content
                return html
            except Exception:
                failed_count += 1
                print ('使用' + str(proxies)  + '获取%s的html失败' %url)
                html = None
        return html
class Proxies():
    def __init__(self):
        self.url = 'http://www.xicidaili.com/nn'
        self.address = u'国内'
        self.verify_keys = {'http://www.7kk.com':'467472408','http://music.163.com/':'27354635321361636375'}
        self.verify_url = ['http://www.7kk.com', 'http://music.163.com/']
        # self.url = 'http://www.xicidaili.com/wn'
        # self.address = u'国外'
    def proxySource(self):
        url_list = []
        for page in range(1, 5):
            url_list.append(self.url + '/' + str(page))
        for url in url_list:
            self.proxyGet(url)

    def proxyGet(self, url):
        html = too.getHtml(url)
        proxiesList = []
        ipList = re.findall(r'td>(\d+\.\d+\.\d+\.\d+)</td>', html.decode('utf-8'))
        kouList = re.findall(r'td>(\d+)</td', html.decode('utf-8'))
        for index in range(0, len(ipList) - 1):
            proxiesList.append(ipList[index] + ':' + kouList[index])
        print ('获取到' + str(len(proxiesList)) + '条代理')
        for proxy in proxiesList:
            proxyDict = {}
            proxyDict['proxy'] = proxy
            proxyDict['Address'] = self.address
            mon.collection.insert(proxyDict)
        print (str(len(proxiesList)) + '条代理录入到SourceIp中')

    def proxyTest(self):
        sourceIpDicts = mon.collection.find({'Address': self.address})
        pool = ThreadPool(8)
        pool.map(self.proxyTestPro, sourceIpDicts)
        pool.close()
        pool.join()

    def proxyTestPro(self, proxySourceDict):
        proxies = {}
        proxies['http'] = 'http://' + str(proxySourceDict['proxy'])
        if too.getHtml('http://www.ip138.com',proxies=proxies) and mon.collection_3.find({'proxy':proxySourceDict['proxy']}).count() == 0:
            proxyDict = {}
            proxyDict['proxy'] = proxySourceDict['proxy']
            proxyDict['type'] = 'hide'
            proxyDict['Address'] = self.address
            proxyDict['datetime'] = datetime.datetime.now()
            proxyDict['ttl'] = 0
            mon.collection_3.insert(proxyDict)
            print (str(proxySourceDict['proxy']) + '代理有效')
        mon.collection.remove({'proxy':proxySourceDict['proxy']})

    def keepUsefulMain(self):
        proxiesDicts = mon.collection_3.find({'Address': self.address})
        for proxy in proxiesDicts:
            self.keepUseful(proxy)

        proxiesDicts = mon.collection_2.find({'Address': self.address})
        for proxy in proxiesDicts:
            self.keepUseful(proxy)

    def keepUseful(self, proxyDict):
        # 用于验证的网站
        canVisit = ''
        try:
            mon.collection_2.remove({'proxy': proxyDict['proxy']})
        except Exception:
            pass
        for each_verify_url in self.verify_url: # 验证每一个网站
            verify_key = self.verify_keys[each_verify_url]
            proxies = {}
            proxies['http'] = 'http://' + str(proxyDict['proxy'])
            html = too.getHtml(each_verify_url, proxies=proxies) # 获取验证网站的html

            if html and (html.decode('utf-8')).find(verify_key) >= 0: # 判断获取的html是否正确
                print (str(proxyDict['proxy']) + '代理有效')
                canVisit += each_verify_url
            else:
                print (str(proxyDict['proxy']) + '代理无法访问%s' % str(each_verify_url))
        if canVisit:
            print('%s可访问的网站，有%s' % (proxyDict['proxy'], canVisit))
            mon.collection_3.update({'proxy': proxyDict['proxy']},
                                    {'$set': {'datetime': datetime.datetime.now(), 'canVisit': canVisit}})
        else:
            try:
                mon.collection_3.remove({'proxy': proxyDict['proxy']})
            except KeyError:
                pass
    def outPutIp(self):
        ipDicts = mon.collection_2.find()
        ipList = []
        for ipDict in ipDicts:
            ipList.append(ipDict['proxy'])
        with open('ipList.txt', 'w') as fl:
            for ip in ipList:
                fl.write(ip + '\n')
        fl.close()
        print ('导出代理完成')

    def get_one_proxy(self, ip_collection=None, ip_key=None):
        if not ip_collection:
            count = mon.collection.find().count()
            random_count = random.randint(0, count - 1)
            proxy_dict = mon.collection.find()[random_count]
            proxy = proxy_dict['proxy']
            proxies = {'http':'http://%s' %str(proxy)}
        else:
            count = ip_collection.find().count()
            random_count = random.randint(0, count - 1)
            proxy_dict = ip_collection.find()[random_count]
            proxy = proxy_dict[ip_key]
            proxies = {'http':'http://%s' %str(proxy)}
        return proxies

    def get_random_proxy(self):
        count = mon.collection_2.find().count()
        if count > 0:
            proxy_dict = mon.collection_2.find()[random.randint(0, count - 1)]
            if random.randint(0, 100) > 10:
                proxies = {'http':'http://%s' % str(proxy_dict['proxy'])}
            else:
                proxies = None
            return proxies
class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Proxy
        self.collection = self.db.SourceIp
        self.collection_2 = self.db.Ip
        self.collection_3 = self.db.TempIp
if __name__ == '__main__':
    ua = UserAgent()
    too = Tool()
    pro = Proxies()
    mon = Mongo()
    pro.proxySource()
    pro.proxyTest()
    pro.keepUsefulMain()
    #pro.outPutIp()
    #print pro.get_random_proxy()

else:
    too = Tool()
    pro = Proxies()
    mon = Mongo()
