from lxml import etree
from pymongo import MongoClient
from GetHtml import hp
from MongoManagement import mon
from multiprocessing.dummy import Pool as ThreadingPool
import datetime, time

class ProxyGet:
    def __init__(self):
        self.urls = {'xici':'http://www.xicidaili.com/wt/page',
                     'kuai':'http://www.kuaidaili.com/free/inha/page/',
                     }

    def get_source_from_html_xici(self, url):
        if url.find('page') > 0:
            _url = url.replace('page', '1')
        else:
            _url = url
        html = hp.get_html(_url).text
        print('获取到%s的html' % _url)
        if self.parse_links_xici(html):
            this_page = _url.split('/')[-1]
            next_url = _url.replace(this_page, str(int(this_page) + 1))
            self.get_source_from_html_xici(next_url)
        else:
            print('获取到昨天的代理ip，停止获取')

    def parse_links_xici(self, html):
        xpath_html = etree.HTML(html)
        today_date = str(datetime.date.today())[2:]
        # 定义一个日期判断bool值，根据日期判断是否要继续，在for循环中每次获取ip都进行判断
        # 日期不等直接return false，相等则继续
        date_judge = False
        for each_tr_tag in xpath_html.xpath('//*[@id="ip_list"]/tr')[1:]:
            ip_dict = {}
            ip_dict['proxy'] = each_tr_tag.xpath('td[2]/text()')[0] + ':' + each_tr_tag.xpath('td[3]/text()')[0]
            ip_dict['type'] = each_tr_tag.xpath('td[6]/text()')[0]
            ip_dict['time'] = each_tr_tag.xpath('td[10]/text()')[0]

            date_judge = ip_dict['time'].split(' ')[0] == today_date
            if date_judge:
                mon.insert_dict(ip_dict, mop.sourceProxies)
            else:
                return date_judge

        print('将该页html中的SourceProxies存入数据库中')
        return date_judge

    def get_source_from_html_kuai(self, url):
        if url.find('page') > 0:
            _url = url.replace('page', '1')
        else:
            _url = url
        html = hp.get_html(_url).text
        print('获取到%s的html' % _url)
        if self.parse_links_kuai(html):
            this_page = _url.split('/')[-2]
            next_url = _url.replace(this_page, str(int(this_page) + 1))
            self.get_source_from_html_kuai(next_url)
        else:
            print('获取到昨天的代理ip，停止获取')

    def parse_links_kuai(self, html):
        xpath_html = etree.HTML(html)
        today_time = str(datetime.date.today())
        for each_tr in xpath_html.xpath('//*[@id="list"]/table/tbody/tr'):
            ip_dict = {}
            ip_dict['proxy'] = each_tr.xpath('td[1]/text()')[0] + ':' + each_tr.xpath('td[2]/text()')[0]
            ip_dict['type'] = each_tr.xpath('td[4]/text()')[0]
            ip_dict['time'] = each_tr.xpath('td[7]/text()')[0]
            judge_result = today_time == ip_dict['time'].split(' ')[0]
            if judge_result:
                mon.insert_dict(ip_dict, mop.sourceProxies)
            else:
                return judge_result
        return judge_result
    def main(self):
        # 获取网站上的所有代理
        self.get_source_from_html_xici('http://www.xicidaili.com/nn/page')
        self.get_source_from_html_kuai('http://www.kuaidaili.com/free/inha/page/')
class ProxyCheck:
    def __init__(self):
        self.first_check_url_http = 'http://www.ip138.com'
        self.first_check_url_https = 'https://jinshuju.net/f/YqBTlv'

    # 筛选可用的代理
    def check_http(self, proxy_dict):
        print('验证%s的有效性' % str(proxy_dict['proxy']))
        proxies = {'http': proxy_dict['proxy']}

        if proxy_dict['type'] == 'http':
            html = hp.get_html(self.first_check_url_http, proxies=proxies, retry_time=2)
        else:
            html = hp.get_html(self.first_check_url_https, proxies=proxies, retry_time=2)
        # 先判定是否有response
        if not html:
            return False
        # response不为空， 判定是否获取正确
        if proxy_dict['type'] == 'http':
            try:
                xpath_html = etree.HTML(html.content.decode('gb2312'))
                title = xpath_html.xpath('/html/head/title/text()')[0]
                if title == 'IP地址查询--手机号码查询归属地 | 邮政编码查询 | 长途电话区号 | 身份证号码验证在线查询网':
                    print('哈哈哈哈哈哈哈-----------------------')
                    return True
                else:
                    return False
            except Exception:
                return False
        elif proxy_dict['type'] == 'https':
            try:
                xpath_html = etree.HTML(html.content)
                title = xpath_html.xpath('/html/head/title/text()')[0]
                if title == '1':
                    return True
                else:
                    return False
            except Exception:
                return False

    def check_proxy(self, proxy_dict):
        result = self.check_http(proxy_dict)
        # 根据返回的result，保存、移除代理字典
        if result:
            mon.insert_dict(proxy_dict, mop.dealProxies)  # 存入到dealProxies中
            mon.remove_dict({'proxy': proxy_dict['proxy']}, mop.sourceProxies)
            print('代理%s可用' % proxy_dict['proxy'])
        else:
            mon.remove_dict({'proxy': proxy_dict['proxy']}, mop.sourceProxies)
            print('代理%s不可用' % proxy_dict['proxy'])

    def main(self):
        proxy_dicts = mop.sourceProxies.find()
        proxy_list = []
        for each_dict in proxy_dicts:
            proxy_list.append(each_dict)
        pool = ThreadingPool(8)
        pool.map(self.check_proxy, proxy_list)
        pool.close()
        pool.join()

class ProxyManage:
    def manage_proxy(self):
        # 将dealProxy中的代理转移到usefulProxy中一起验证
        print('开始进行有效代理的维护')
        deal_proxy_dicts = mop.dealProxies.find()
        if deal_proxy_dicts.count() > 0:
            for deal_proxy_dict in deal_proxy_dicts:
                mon.insert_dict(self.make_new_dict(deal_proxy_dict), mop.usefulProxies)
                mon.remove_dict({'proxy':deal_proxy_dict['proxy']}, mop.dealProxies)
        useful_proxy_dicts = mop.usefulProxies.find()
        for each_dict in useful_proxy_dicts:
            self.check_store_proxy(each_dict)

    def check_store_proxy(self, proxy_dict):
        # 根据代理的type调用proxyCheck中的方法
        result = proc.check_http(proxy_dict)
        # 根据返回的result，保存、移除代理字典及更新信息
        if result:
            # 代理有效
            live_time = self.count_live_time(proxy_dict['time'])
            proxy_dict['live_time'] = str(live_time)
            # mop.update_dict({'proxy':proxy_dict['proxy']}, {'live':proxy_dict['live_time']}, mop.usefulProxies)
            print('代理%s可用, 更新信息' % proxy_dict['proxy'])
        else:
            # mon.remove_dict({'proxy': proxy_dict['proxy']}, mop.usefulProxies)
            print('代理%s失效' % proxy_dict['proxy'])

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
        new_dict['liveTime'] = '0'
        new_dict['canVisit'] = 'None'
        return new_dict
    # def insert_deal_proxy(self, deal_proxy):

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
if __name__ == '__main__':
    mop = MongoPro()
    prog = ProxyGet()
    proc = ProxyCheck()
    prom = ProxyManage()
    prog.main()
    proc.main()
    prom.manage_proxy()
