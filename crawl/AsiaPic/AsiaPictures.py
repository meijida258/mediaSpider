from tool.GetHtml import hp
from tool.ProxyMantenance import ProxyUse, MongoPro
from pymongo import MongoClient
from lxml import etree
from multiprocessing.dummy import Pool
import queue, re, os, requests

class AsiaStarName:
    def __init__(self):
        self.url = 'http://www.ylq.com/'
        self.type_dicts = {'港台明星':'gangtai/', '内地明星':'neidi/'}
        self.proxy_queue = queue.Queue()
        proxy_dicts = mp.usefulProxies.find({'$and': [{'type': {'$eq': 'http'.upper()}}, {'failed': {'$lt': 10}}]})
        for proxy_dict in proxy_dicts:
            self.proxy_queue.put(proxy_dict['proxy'])

    def get_page_data(self, url):
        proxies = self.proxy_queue.get()
        while True:
            try:
                page_content = hp.get_html(url, proxies)
                self.proxy_queue.put(proxies) # 放回代理
                print('放回代理')
                return page_content
            except Exception:
                failed_proxies = mp.usefulProxies.find({'proxy':proxies})[0]
                if failed_proxies['failed'] >= 8:
                    print('代理错误次数过多，移除队列')
                else:
                    self.proxy_queue.put(proxies)
                    print('放回代理')

    def parse_page_data(self, page_content):
        html = etree.HTML(page_content.content)
        name_list = html.xpath('//*[@class="fContent"]/ul/li/a/h2/text()')
        img_list = html.xpath('//*[@class="fContent"]/ul/li/a/img/@src')
        detail_url_list = html.xpath('//*[@class="fContent"]/ul/li/a/@href')
        num = min(len(name_list), len(img_list))
        result_dicts = []
        for each_index in range(0, num):
            result_dict = {}
            result_dict['name'] = name_list[each_index]
            result_dict['img_0'] = img_list[each_index]
            result_dict['url'] = detail_url_list[each_index]
            result_dicts.append(result_dict)
        # 开启多进程访问每一页中所有人物的图片
        self.threading_control(result_dicts)


    def threading_control(self, result_dicts):
        pool = Pool(8)
        pool.map(self.get_img_from_detail, result_dicts)
        pool.close()
        pool.join()

    def get_img_from_detail(self, result_dict):
        detail_url_content = self.get_page_data(result_dict['url'])
        html = etree.HTML(detail_url_content.content)
        try:
            img_1 = html.xpath('//*[@class="perData"]/div[2]/a/img/@src')[0]
        except Exception:
            img_1 = ""
        result_dict['img_1'] = img_1
        result_dict.pop('url')
        if ms.collection.find({'name': result_dict['name']}).count() == 0:
            ms.collection.insert(result_dict)
            print('录入一条信息')
        return result_dict

    def main(self):
        url = self.url + self.type_dicts['港台明星']
        page_url_list = [url + 'index_%s.html' % page for page in range(27, 32)]
        page_url_list.append('http://www.ylq.com/gangtai/')
        for url in page_url_list:
            page_content = self.get_page_data(url)
            print(url)
            self.parse_page_data(page_content)

class CollectPic:
    def search_360_pic(self, name_dict): # 输入字典，返回图片url
        url = 'https://baike.so.com/search/?q=' + name_dict['name']
        search_result = requests.get(url)
        # 重复获取3次
        num = 0
        html = ''
        while num <= 3:
            if search_result:
                html = etree.HTML(search_result.text)
                break
            else:
                num += 1
        if html:
            try:
                detail_url = re.findall('<a href="(.*?)" target="_blank">%s_360百科</a>' % name_dict['name'], html)[0]
            except Exception:
                return ''
        # 判断url的格式，是移动端还是pc端的
        if detail_url.find('//m.baike.so') > 0:
            detail_url_ = detail_url
        else:
            detail_url_ = detail_url.replace('//baike.so', '//m/baike.so')
        detail_html = requests.get(detail_url_)


class DownLoadPic:
    def __init__(self):
        self.pic_save_path = 'F:/picture'
    def threading_control(self, pic_dict):

        self.create_dir(pic_dict['name'])
        pic_count = 0
        while True:
            img_key = 'img_%s' % str(pic_count)
            try:
                pic_url = pic_dict[img_key]
                pic_content = self.download(pic_url)
                with open(self.pic_save_path + '/' + pic_dict['name'] + '/' + img_key + '.jpg', 'wb') as pic:
                    pic.write(pic_content)
                pic.close()
            except Exception:
                break
            pic_count += 1
        print('下载完毕')

    def main(self):
        pic_dicts =ms.collection.find({'collect_pic':'Yes'})
        for i in pic_dicts:
            self.threading_control(i)
        # pool = Pool(8)
        # pool.map(self.threading_control, pic_dicts)
        # pool.close()
        # pool.join()
    def download(self, pic_url):
        pic_content = requests.get(pic_url).content
        return pic_content

    def create_dir(self, dir_name):
        save_path = self.pic_save_path + '/' + dir_name
        if not os.path.exists(save_path):
            os.mkdir(save_path)

class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Star
        self.collection = self.db.Name

if __name__ == '__main__':
    mp = MongoPro()
    ms = MongoSet()
    asn = AsiaStarName()
    dlp = DownLoadPic()
    # dlp.main()
    asn.main()
