"""
    target_url : http://www.smzdm.com/
    save_DB : SMZDM
    save_collection : Goods
"""
import sys
sys.path.append('..')
from tool.ProxyMantenance import MongoPro, ProxyUse
from tool.GetHtml import HtmlPro
from pymongo import MongoClient
import time, asyncio, queue
import xlwt
class SMZDM:
    def __init__(self):
        self.proxy_queue = queue.Queue()
        proxy_dicts = mp.usefulProxies.find({'$and':[{'type':{'$eq':'http'.upper()}}, {'failed':{'$lt':10}}]})
        for proxy_dict in proxy_dicts:
            self.proxy_queue.put(proxy_dict['proxy'])
        self.need_parse_pages = set()
        self.already_parse_pages = set()
        # 取当前时间作为请求的参数，补够12位。
        self.start_time = int(time.time() * 100)
        # self.start_time = 149683196657
    def get_json(self, url):
        while True:
            proxies = self.proxy_queue.get()
            if self.proxy_queue.empty():
                print('无可用代理')
                exit()
            print('队列中取出%s作为代理' % str(proxies))
            try:
                response_json = hp.get_html(url,
                              add_headers={'Referer':'http://www.smzdm.com/jingxuan/',
                                           'X-Requested-With':'XMLHttpRequest',
                                           'Host':'www.smzdm.com'},
                                            timeout=30,
                                            proxies={'http':'http://%s' % proxies}).json()
                self.proxy_queue.put(proxies)
                print('放回代理')
                if response_json:
                    return response_json
                else:
                    prou.update_used_proxy(proxies, False)
            except:
                failed_proxies = mp.usefulProxies.find({'proxy':proxies})[0]
                if failed_proxies['failed'] >= 8:
                    print('%s失败次数过多，移出队列' % proxies)
                else:
                    self.proxy_queue.put(proxies)
                print('放回代理')
                prou.update_used_proxy(proxies, False)
                print('请求有问题，重新链接')

    def parse_goods(self, page_json):
        print('json数据获取完成，记录需要的信息')
        # 获取json中的所有有用信息
        time_sort = ''
        for each_item in page_json:
            result = {}
            try:
                result['goods_category'] = each_item['article_category']['nicktitle']
            except TypeError:
                result['goods_category'] = ''
            except:
                result['goods_category'] = each_item['article_category']['url_nicktitle']
            result['goods_name'] = each_item['article_title']
            result['goods_url'] = each_item['article_url']
            result['time_sort'] = each_item['timesort']
            time_local = time.localtime(int(result['time_sort']/100))
            result['goods_date'] = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
            try:
                result['goods_price'] = each_item['article_price']
            except:
                result['goods_price'] = ''
            try:
                result['goods_from'] = each_item['article_mall']
            except:
                result['goods_from'] = ''
            # 判断该物品是否已存在
            if mon.goods_collection.find({'goods_url':result['goods_url'], 'time_sort':result['time_sort']}).count() == 0:
                mon.goods_collection.insert(result)
            else:
                print('获取到重复的信息，结束')
                exit()
            time_sort = result['time_sort']
        return time_sort

    def main_loop(self, time_sort):
        time_local = time.localtime(int(time_sort/100))
        print('开始获取%s之后的20个商品' % time.strftime("%Y-%m-%d %H:%M:%S",time_local))
        url = 'http://www.smzdm.com/json_more?timesort={}'.format(time_sort)
        page_json = self.get_json(url)
        next_time_sort = self.parse_goods(page_json)
        self.main_loop(next_time_sort)

    def main(self):
        self.main_loop(self.start_time)


class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.SMZDM
        self.goods_collection = self.db.Goods


if __name__ == '__main__':
    mp = MongoPro()
    prou = ProxyUse()
    hp = HtmlPro()
    mon = Mongo()
    sm = SMZDM()

    # dagmain()
    sm.main()
