from lxml import etree
from pymongo import MongoClient
from GetHtml import hp
from MongoManagement import mon
from multiprocessing.dummy import Pool as ThreadingPool
import datetime, time, random
import asyncio, aiohttp
import requests, re

class ProxyGet:
    def __init__(self):
        self.urls = {'xici':'http://www.xicidaili.com/nn/page',
                     'kuai':'http://www.kuaidaili.com/free/inha/page/',
                     }
        self.xici_headers = {
                       'Referer':'http://www.xicidaili.com/nn/',
                       'Host':'www.xicidaili.com'
                   }

    def get_proxies(self):
        proxy_dicts = mop.usefulProxies.find()
        proxy_count = proxy_dicts.count()
        while True:
            proxy_dict = proxy_dicts[random.randint(0, proxy_count - 1)]
            if int(proxy_dict['live_time']) > 30:
                return {'http':'http://%s' % proxy_dict['proxy']}
            else:
                pass

    def get_source_from_html_xici(self, url):
        print(url)
        if url.find('page') > 0:
            _url = url.replace('page', '1')
        else:
            _url = url
        retry_count = 0
        while retry_count < 10:
            if retry_count == 9:
                proxies = {}
            else:
                proxies = self.get_proxies()
            try:

                result = hp.get_html(_url, proxies=proxies, add_headers=self.xici_headers)
                print(result)
                if result:
                    html = result.text
                    break
                else:
                    if retry_count < 10:
                        print('获取%s失败，重试%s次' %(_url, str(retry_count)))
                        retry_count += 1
                        html = ''
            except Exception as e:
                print(e)
                html = ''
        if not html and retry_count >= 10:
            return
        print('获取到%s的html' % _url)
        # 以获取到的ip数量，判断是否结束
        if mop.sourceProxies.find().count() > 4500:
            return
        # 以获取到的ip时间，判断是否结束
        if self.parse_links_xici(html):
            this_page = _url.split('/')[-1]
            next_url = _url.replace(this_page, str(int(this_page) + 1))
            self.get_source_from_html_xici(next_url)
        else:
            print('获取到昨天的代理ip，停止获取')

    def parse_links_xici(self, html):
        xpath_html = etree.HTML(html)
        today_date = str(datetime.date.today())[2:]
        yesterday_date = today_date.replace(today_date[-2:], str(int(today_date[-2:]) - 1))
        # 定义一个日期判断bool值，根据日期判断是否要继续，在for循环中每次获取ip都进行判断
        # 日期不等直接return false，相等则继续
        date_judge = False
        for each_tr_tag in xpath_html.xpath('//*[@id="ip_list"]/tr')[1:]:
            ip_dict = {}
            try:
                ip_dict['proxy'] = each_tr_tag.xpath('td[2]/text()')[0] + ':' + each_tr_tag.xpath('td[3]/text()')[0]
                ip_dict['type'] = each_tr_tag.xpath('td[6]/text()')[0]
                ip_dict['time'] = each_tr_tag.xpath('td[10]/text()')[0]

                date_judge = ip_dict['time'].split(' ')[0] != yesterday_date
                if date_judge:
                    mon.insert_dict(ip_dict, mop.sourceProxies, 'proxy')
                else:
                    return date_judge
            except:
                return False

        print('将该页html中的SourceProxies存入数据库中')
        return date_judge

    def get_source_from_html_kuai(self, url):
        if url.find('page') > 0:
            _url = url.replace('page', '1')
        else:
            _url = url
        while True:
            html = hp.get_html(_url)
            if html:
                break
            else:
                return
        print('获取到%s的html' % _url)
        if self.parse_links_kuai(html.text):
            this_page = _url.split('/')[-2]
            next_url = _url.replace(this_page, str(int(this_page) + 1))
            self.get_source_from_html_kuai(next_url)
        else:
            print('获取到昨天的代理ip，停止获取')

    def parse_links_kuai(self, html):
        xpath_html = etree.HTML(html)
        today_time = str(datetime.date.today())
        yesterday_date = today_time.replace(today_time[-2:], str(int(today_time[-2:]) - 1))
        for each_tr in xpath_html.xpath('//*[@id="list"]/table/tbody/tr'):
            ip_dict = {}
            ip_dict['proxy'] = each_tr.xpath('td[1]/text()')[0] + ':' + each_tr.xpath('td[2]/text()')[0]
            ip_dict['type'] = each_tr.xpath('td[4]/text()')[0]
            ip_dict['time'] = each_tr.xpath('td[7]/text()')[0]
            judge_result = yesterday_date == ip_dict['time'].split(' ')[0]
            if judge_result:
                mon.insert_dict(ip_dict, mop.sourceProxies, 'proxy')
            else:
                return judge_result
        return judge_result

    def gatherprorxy_control(self):
        for page in range(1, 6):
            html = self.get_source_from_html_gatherproxy(page)
            # print(html)
            if html:
               self.parse_links_gather(html)

    def get_source_from_html_gatherproxy(self, page):
        headers = {
            'Host': "www.gatherproxy.com",  # 需要修改为当前网站主域名
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0",
            "referer": 'http://www.gatherproxy.com/zh/proxylist/country/?c=China'  # 随意的伪造值
        }
        try_count = 1
        while try_count < 5:
            try:
                html = requests.post('http://www.gatherproxy.com/zh/proxylist/country/?c=china',proxies={'http': 'http://192.168.2.100:8081'}, headers=headers,data={"Country": "china", "PageIdx": str(page)}).text
                return html
            except:
                try_count += 1
        return None

    def parse_links_gather(self, html):
        ip_list = re.findall(r"document\.write\('(.*?)'\)", html)
        port_list = re.findall(r"document\.write\(gp\.dep\('(.*?)'\)\)", html)
        if len(ip_list) != len(port_list) or not ip_list or not port_list:
            return
        for ip in ip_list:
            ip_dict = {}
            ip_dict['proxy'] = ip + ':' + str(int(port_list[ip_list.index(ip)], 16))
            ip_dict['type'] = 'HTTP'
            ip_dict['time'] = str(datetime.datetime.now())[2:-10]
            mon.insert_dict(ip_dict, mop.sourceProxies, 'proxy')

    def main(self):
        # 获取网站上的所有代理
        self.get_source_from_html_xici('http://www.xicidaili.com/nn/page')
        self.gatherprorxy_control()
        # self.get_source_from_html_kuai('http://www.kuaidaili.com/free/inha/page/')
class ProxyCheck:
    def __init__(self):
        self.first_check_url_http = 'http://www.7kk.com'
        self.first_check_url_https = 'https://jinshuju.net/f/YqBTlv'

    # 筛选可用的代理
    def check_http(self, proxy_dict):
        print('验证%s的有效性' % str(proxy_dict['proxy']))


        if proxy_dict['type'].lower() == 'http':
            proxies = {'http': 'http://%s' % proxy_dict['proxy']}
            html = hp.get_html(self.first_check_url_http, proxies=proxies, retry_time=2, timeout=30)
        else:
            proxies = {'https': 'http://%s' % proxy_dict['proxy']}
            html = hp.get_html(self.first_check_url_https, proxies=proxies, retry_time=2, timeout=30)
        # 先判定是否有response
        if not html:
            return False
        # response不为空， 判定是否获取正确
        if proxy_dict['type'].lower() == 'http':
            try:
                xpath_html = etree.HTML(html.content.decode('utf-8'))
                title = xpath_html.xpath('/html/head/title/text()')[0]
                if title == '美女图片写真 性感美女图片大全-7kk美女图片':
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                return False
        elif proxy_dict['type'].lower() == 'https':
            try:
                xpath_html = etree.HTML(html.content)
                # print(html.content)
                title = xpath_html.xpath('/html/head/title/text()')[0]
                if title == '1':
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                return False

    def check_proxy(self, proxy_dict):
        result = self.check_http(proxy_dict)
        # 根据返回的result，保存、移除代理字典
        if result:
            if mop.dealProxies.find({'proxy':proxy_dict['proxy']}).count() == 0:
                mon.insert_dict(proxy_dict, mop.dealProxies)  # 存入到dealProxies中
            else:
                print('代理%s已存在' % proxy_dict['proxy'])
            mon.remove_dict({'proxy': proxy_dict['proxy']}, mop.sourceProxies)
            print('代理%s可用' % proxy_dict['proxy'])
        else:
            mon.remove_dict({'proxy': proxy_dict['proxy']}, mop.sourceProxies)
            print('代理%s不可用' % proxy_dict['proxy'])

    def main(self):
        # 对获取的代理进行验证
        proxy_dicts = mop.sourceProxies.find()
        proxy_list = []
        for each_dict in proxy_dicts:
            proxy_list.append(each_dict)
        pool = ThreadingPool(8)
        pool.map(self.check_proxy, proxy_list)
        pool.close()
        pool.join()

class ProxyCheck_:
    def __init__(self):
        # http://www.yxkfw.com/?fromuid=87246     http://1212.ip138.com/ic.asp
        self.test_urls = {'http':'http://www.ip138.com/',
                          'https':'https://jinshuju.net/f/YqBTlv'}

    async def manage_proxy(self, proxy_dict, result):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.test_urls[proxy_dict['type'].lower()], proxy=(proxy_dict['type'].lower() + '://' + proxy_dict['proxy']), timeout=30) as response:
                    result.append({'proxy_dict':proxy_dict, 'status':response.status})
            except:
                result.append({'proxy_dict':proxy_dict, 'status':10060})

    def check_proxy(self, result_dict):
        # 根据返回的result，保存、移除代理字典
        if result_dict['status'] == 200:
            if mop.dealProxies.find({'proxy':result_dict['proxy_dict']['proxy']}).count() == 0:
                mon.insert_dict(result_dict['proxy_dict'], mop.dealProxies)  # 存入到dealProxies中
            else:
                print('代理%s已存在' % result_dict['proxy_dict']['proxy'])
            mon.remove_dict({'proxy': result_dict['proxy_dict']['proxy']}, mop.sourceProxies)
            print('代理%s可用' % result_dict['proxy_dict']['proxy'])
        else:
            mon.remove_dict({'proxy': result_dict['proxy_dict']['proxy']}, mop.sourceProxies)
            print('代理%s不可用' % result_dict['proxy_dict']['proxy'])

    def do_get(self):
        proxy_dicts = mop.sourceProxies.find()
        print('当前获得的未测试代理ip数为：{}'.format(proxy_dicts.count()))
        if proxy_dicts.count() > 500:
            result = list(proxy_dicts)[:500]
            return result
        elif proxy_dicts.count() == 0:
            return None
        else:
            return list(proxy_dicts)

    def main(self):
        proxy_dicts = self.do_get()
        if not proxy_dicts:
            return
        print('正在测试的代理ip数为：{}'.format(len(proxy_dicts)))
        loop = asyncio.get_event_loop()
        result = []
        tasks = [self.manage_proxy(proxy_dict, result) for proxy_dict in proxy_dicts]
        loop.run_until_complete(asyncio.wait(tasks))
        for each_result in result:
            self.check_proxy(each_result)
        self.main()
class ProxyManage_:
    def __init__(self):
        self.test_urls = {'http':'http://www.ip138.com/',
                          'https':'https://jinshuju.net/f/YqBTlv',}
    def count_live_time(self, str_time):
        live_time = ((int(time.strftime('%m', time.localtime())) - int(str_time.split(' ')[0].split('-')[1])) * 30 +
                     (int(time.strftime('%d', time.localtime())) - int(str_time.split(' ')[0].split('-')[2]))) * 24 + \
                    (int(time.strftime('%H', time.localtime())) - int(str_time.split(' ')[1].split(':')[0]))
        return live_time

    def make_new_dict(self, deal_proxy_dict):
        new_dict = {}
        new_dict['type'] = deal_proxy_dict['type']
        new_dict['time'] = deal_proxy_dict['time']
        new_dict['proxy'] = deal_proxy_dict['proxy']
        new_dict['live_time'] = '0' # 存活时间
        new_dict['canVisit'] = 'None'
        new_dict['failed'] = 0
        new_dict['succeed'] = 0
        return new_dict

    def update_data(self, result_dict):
        if result_dict['status'] == 200:
            live_time = self.count_live_time(result_dict['proxy_dict']['time'])
            result_dict['proxy_dict']['live_time'] = str(live_time)
            mop.update_dict({'proxy': result_dict['proxy_dict']['proxy']},
                            {'live_time': result_dict['proxy_dict']['live_time'], 'succeed': result_dict['proxy_dict']['succeed'] + 1},
                            mop.usefulProxies)
            print('代理%s可用, 更新信息' % result_dict['proxy_dict']['proxy'])
            # 根据代理类型返回相应值，用于结束时总结
            if result_dict['proxy_dict']['type'].lower() == 'http':
                return 1  # http有效
            else:
                return 2  # https有效
        else:
            # failed+1
            if result_dict['proxy_dict']['failed'] + 1 > 3:
                if result_dict['proxy_dict']['succeed'] <= 3:
                    mon.remove_dict({'proxy': result_dict['proxy_dict']['proxy']}, mop.usefulProxies)
                    print('代理%s失效' % result_dict['proxy_dict']['proxy'])
                else:
                    # pass
                    mop.usefulProxies.update({'proxy':result_dict['proxy_dict']['proxy']}, {'$set':{'succeed':0}})
                if result_dict['proxy_dict']['type'].lower() == 'http':
                    return 3 # http代理失败数，超过3次
                else:
                    return 4 # https代理失败数，超过3次
            else:
                mop.update_dict({'proxy': result_dict['proxy_dict']['proxy']}, {'failed':result_dict['proxy_dict']['failed'] + 1}, mop.usefulProxies)
                print('代理%s访问失败， failed次数+1' % result_dict['proxy_dict']['proxy'])
                if result_dict['proxy_dict']['type'].lower() == 'http':
                    return 5 # http代理失败数+1
                else:
                    return 6 # https代理失败数+1

    async def manage_proxy(self, proxy_dict, result):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.test_urls[proxy_dict['type'].lower()], proxy=(proxy_dict['type'].lower() + '://' + proxy_dict['proxy']), timeout=30) as response:
                    result.append({'proxy_dict':proxy_dict, 'status':response.status})
            except:
                result.append({'proxy_dict':proxy_dict, 'status':10060})

    def write_note(self, note_result, start_time):
        useful_http, useful_https, failed_http, failed_https, remove_http, remove_https = 0, 0, 0, 0, 0, 0
        for each_return in note_result:
            if each_return == 1:
                useful_http += 1
            elif each_return == 2:
                useful_https += 1
            elif each_return == 3:
                remove_http += 1
            elif each_return == 4:
                remove_https += 1
            elif each_return == 5:
                failed_http += 1
            elif each_return == 6:
                failed_https += 1
        print('验证完成，耗时%s，结果如下：' % str(time.time() - start_time))
        print('有效代理数：http共%s个， https共%s个' % (str(useful_http), str(useful_https)))
        print('失效代理数：http共%s个， https共%s个' % (str(remove_http), str(remove_https)))
        print('访问失败代理数：http共%s个， https共%s个' % (str(failed_http), str(failed_https)))
        with open('proxy_manage.txt', 'a') as fl:
            fl.write('%s代理维护结果如下-------------------------%s' % (str(datetime.date.today()), '\n'))
            fl.write('有效代理数：http共%s个， https共%s个%s' % (str(useful_http), str(useful_https), '\n'))
            fl.write('失效代理数：http共%s个， https共%s个%s' % (str(remove_http), str(remove_https), '\n'))
            fl.write('访问失败代理数：http共%s个， https共%s个%s' % (str(failed_http), str(failed_https), '\n'))
        fl.close()

    def main_loop(self, useful_proxy_dicts, start_time):
        result = []
        tasks = [self.manage_proxy(proxy, result) for proxy in useful_proxy_dicts]
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(asyncio.wait(tasks))
        return result

    def main(self):
        start_time = time.time()
        # 获取所有的有效代理
        print('开始进行有效代理的维护')
        #先把deal里的ip放进useful里面
        deal_proxy_dicts = mop.dealProxies.find()
        if deal_proxy_dicts.count() > 0:
            for deal_proxy_dict in deal_proxy_dicts:

                mon.insert_dict(self.make_new_dict(deal_proxy_dict), mop.usefulProxies, 'proxy')
                mon.remove_dict({'proxy':deal_proxy_dict['proxy']}, mop.dealProxies)
        useful_proxy_dicts_temp = mop.usefulProxies.find(no_cursor_timeout=True)
        useful_proxy_dicts = []
        for i in useful_proxy_dicts_temp:
            useful_proxy_dicts.append(i)
        #
        result = []
        callback_time = 0
        while True:
            try:
                temp_useful_proxy_dicts = useful_proxy_dicts[callback_time*500:(callback_time+1)*500]
            except:
                temp_useful_proxy_dicts = useful_proxy_dicts[callback_time * 500:]
            if len(temp_useful_proxy_dicts) == 0:
                break
            temp_result = []
            for each_result in self.main_loop(temp_useful_proxy_dicts, temp_result):
                result.append(each_result)
            callback_time += 1
        note_result = []
        for each_result in result:
            note_result.append(self.update_data(each_result))
        self.write_note(note_result, start_time)

class MongoPro:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Proxy
        # 未筛选的ip存储在mongo中的Source中
        self.sourceProxies = self.db.SourceProxy
        # 第一步筛选过的ip存储到DealProxy中
        self.dealProxies = self.db.DealProxy
        # 最终存入的常用ip中
        self.usefulProxies = self.db.UsefulProxy

    def update_dict(self, verify_dict, update_dict, target_collection):
        target_collection.update(verify_dict, {'$set':update_dict})
        print('更新一条信息')

class ProxyUse:
    def get_random_proxy(self, type):
        proxy_dicts = mop.usefulProxies.find({'type':type.upper()})
        # 返回一个符合要求的代理
        while True:
            try:
                proxy_dict = proxy_dicts[random.randint(0, proxy_dicts.count())]
                break
            except Exception as e:
                print(e)
        if random.randint(0, 100) > 10:
            result = {type:'http://%s' % proxy_dict['proxy']}
        else:
            result = {}
        return result

    def get_all_proxy(self, type):
        # 返回符合要求的所有代理
        proxy_dicts = mop.usefulProxies.find({'type':type.upper()})
        result = []
        for proxy_dict in proxy_dicts:
            result.append({'http':'http://%s' % proxy_dict['proxy']})
        return result

    def update_used_proxy(self, proxy, result): # 返回使用的结果，更新代理的状态
        try:
            proxy_dict = mop.usefulProxies.find({'proxy': proxy})[0]
        except IndexError:
            print('没有找到这个代理')
            return
        if result == 'success':
            # 更新代理存活时间
            live_time = prom.count_live_time(proxy_dict['time'])
            proxy_dict['live_time'] = str(live_time)
            mop.update_dict({'proxy': proxy}, {'live_time': proxy_dict['live_time']}, mop.usefulProxies)
        else:
            # 失败次数+1，并记录
            failed_count = proxy_dict['failed'] + 1
            if failed_count > 5:
                # 失败次数超过上限，删除
                mop.usefulProxies.remove({'proxy':proxy})
            else:
                # 失败次数未超上限，更新记录
                mop.usefulProxies.update({'proxy': proxy},{'$set':{'failed':failed_count}})

    def get_proxy_queue(self, type):
        proxy_dicts = mop.usefulProxies.find({'type': type.upper()})

if __name__ == '__main__':
    mop = MongoPro()
    prog = ProxyGet()
    proc_ = ProxyCheck_()  # 异步    proc = ProxyCheck() # 多进程
    prom_ = ProxyManage_() # 异步    prom = ProxyManage() # 多进程
    prou = ProxyUse()
    prog.main()
    proc_.main()
    prom_.main()
    # print(mop.sourceProxies.find().count())
else:
    mop = MongoPro()
    prog = ProxyGet()
    prou = ProxyUse()
