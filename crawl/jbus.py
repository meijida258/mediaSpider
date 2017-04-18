import sys, re, random, requests, os, datetime
sys.path.append('..')
from tool.GetHtml import HtmlPro
from tool.MongoManagement import MongoSet
from lxml import etree
from pymongo import MongoClient
# from ..tool.GetHtml import HtmlPro
BASE_URL = 'https://www.javbus.cc/'
PROXIES = {'http':'http://127.0.0.0:1080'}
STAR_URL = 'https://www.javbus.cc/star/'
SERIES_URL = 'https://www.javbus.cc/series/'
TXT_MAGNET_LIST = [] # 用于输出的list

class BusMagnet:
    def __init__(self):
        self.base_url = BASE_URL
        self.proxies = PROXIES

    def get_video_params(self, video_url):
        print('获取%s的表单数据' % video_url)
        target_url = video_url
        while True:
            html = hp.get_html(target_url, self.proxies)
            if html:
                 break
        params = {}
        tvar_args = re.findall('<script>\r\n\tvar gid = (.*?);\r\n\tvar uc = (.);\r\n\tvar img = \'(.*?)\';\r\n</script>', html.text)
        params['gid'] = tvar_args[0][0]
        params['uc'] = tvar_args[0][1]
        params['img'] = tvar_args[0][2]
        params['lang'] = 'zh'
        params['floor'] = str(random.randint(100, 999))
        return params

    def get_movie_magnet(self, params, video_url):
        print('获取%s的magnet' % video_url)
        get_magnet_url = 'https://www.javbus.cc/ajax/uncledatoolsbyajax.php'
        referer = video_url
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                   'Referer':referer}
        while True:
            try:
                result = requests.get(get_magnet_url, headers=headers, params=params).text
                break
            except Exception as e:
                print('错误信息: %s' % e)
        return result

    def deal_magnet(self, movie_magnet_html, video_url):
        print('处理%s获取的magnet' % video_url)
        html = etree.HTML(movie_magnet_html)
        td_list = html.xpath('//*[@style="text-align:center;white-space:nowrap"]')
        result = []
        for index in range(0, int(len(td_list) / 2)):
            magnet_dict = {}
            magnet_dict['magnet'] = td_list[index * 2].xpath('a/@href')[0]
            size = td_list[index * 2].xpath('a/text()')[0]
            magnet_dict['size'] = re.findall(r'\t(.*?) ', size)[0]
            time = td_list[index * 2 - 1].xpath('a/text()')[0]
            magnet_dict['time'] = re.findall(r'\t(.*?) ', time)[0]
            magnet_dict['url'] = video_url
            result.append(magnet_dict)
        return result

    def pick_magnet(self, movie_magnet_list, video_url):
        print('选取%s获取的magnet' % video_url)
        # for each_dict in movie_magnet_list:
        # # 优先中文
        #     if each_dict['magnet'].lower().find('cavi') > 0:
        #         return each_dict
        # # 其次mkv
        # for each_dict in movie_magnet_list:
        #     if each_dict['magnet'].lower().find('mkv') > 0:
        #         return each_dict
        # # 再次avi
        # for each_dict in movie_magnet_list:
        #     if each_dict['magnet'].lower().find('avi') > 0:
        #         return each_dict
        # # 最次MP4
        # for each_dict in movie_magnet_list:
        #     if each_dict['magnet'].lower().find('mp4') > 0:
        #         return each_dict
        #  # 都没有就返回第一个
        # return movie_magnet_list[0]
        weight_dict = {}
        for each_dict in movie_magnet_list:
            weight = 0
            # 大小加分
            if each_dict['size'].lower().find('m'):
                weight += (int(each_dict['size'].lower().split('m')[0]) / 1024 * 5)
            # dvd扣分
            if each_dict['magnet'].lower().find('dvd') > 0 or each_dict['magnet'].lower().find('iso') > 0:
                weight -= 100
            # 中文加分
            if each_dict['magnet'].lower().find('cavi') > 0:
                weight += 100
            # avi mkv mp4 加分
            if each_dict['magnet'].lower().find('avi') > 0 or each_dict['magnet'].lower().find('mkv') > 0 or each_dict['magnet'].lower().find('mp4') > 0:
                weight += 10
            weight_dict[movie_magnet_list.index(each_dict)] = weight

    def main(self, url):
        print('获取%s的磁力字典' % url)
        params = self.get_video_params(url)
        magnet_response = self.get_movie_magnet(params, url)
        magnet_list = self.deal_magnet(magnet_response, url)
        magnet_dict = self.pick_magnet(magnet_list, url)
        return magnet_dict

class BusFind:
    def __init__(self):
        self.star_base = STAR_URL
        self.series_base = SERIES_URL
        self.proxies = PROXIES

    def find_by(self, url):
        print('开始查找代码为%s的作品' % url.split('/')[-2])
        page_parse_result = self.parse_html(url)
        # 返回的该页所有链接，类型为list
        movie_index_list = page_parse_result['xpath_links']
        # 挨个访问获取magnet，并保存
        self.insert_magnet(movie_index_list, url)
        # 返回该页是否有下一页
        next_page = page_parse_result['xpath_next_page']
        if next_page:
            # 有下一页则迭代
            self.find_by_start(next_page)
        else:
            # 没有下一页，结束
            print('查找完成')

    def parse_html(self, url):
        while True:
            print('解析%s的页面信息' % url)
            html = hp.get_html(url, self.proxies)
            if html:
                break
        xpath_html = etree.HTML(html.text)
        xpath_links = xpath_html.xpath('//*[@id="waterfall"]/div/a/@href')
        try:
            xpath_next_page = xpath_html.xpath('//*[@id="next"]/@href')[0]
        except IndexError:
            xpath_next_page = None
        result = {}
        result['xpath_links'] = xpath_links
        result['xpath_next_page'] = xpath_next_page
        return result

    def insert_magnet(self, movie_index_list, url):
        find_type = url.split('/')[-3]
        find_num = url.split('/')[-2]
        for each_link in movie_index_list:
            if mp.collection.find({'url':each_link}).count() == 0:
                insert_dict = bm.main(each_link) # 通过bm类的main函数获取该链接的磁链信息字典
                # 完善字典
                insert_dict['find_type'] = find_type
                insert_dict['find_num'] = find_num
                # 储存字典
                ms.insert_dict(insert_dict, mp.collection, 'url')
                if int(str(datetime.date.today()).split('-')[0]) - int(str(insert_dict['time']).split('-')[0]) < 10:
                    # 大于10年的不输出
                    TXT_MAGNET_LIST.append(insert_dict['magnet']) # 储存到要输出的txt中定义的list中
            else:
                print('%s的相关信息已存在, 跳过该条' % each_link)

class MongoPro:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.JavBusDB
        self.collection = self.db.Magnet

class TextOutPut:
    def __init__(self):
        self.text_path = 'C:/Users/Administrator/Desktop/magnet.txt'


    def out_put_txt(self):
        # if os.path.exists(self.text_path):
        with open(self.text_path, 'w') as fl:
            for magnet in TXT_MAGNET_LIST:
                fl.write(magnet)
                fl.write('\n')
        fl.close()

if __name__ == '__main__':
    top = TextOutPut()
    mp = MongoPro()
    ms = MongoSet()
    hp = HtmlPro()
    bm = BusMagnet()
    bf = BusFind()
    # ----查找----
    # bf.find_by(STAR_URL + 'ngv' + '/1') # 名字查找
    # # bf.find_by(SERIES_URL + 'okq' + '/1')  # 系列查找
    # # ----测试----
    # top.out_put_txt()
    a = {1:100, 2:23, 3:145}
    print(sorted(a.items(), key=lambda item:item[1]))