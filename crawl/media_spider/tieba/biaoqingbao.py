# -*- coding: UTF-8 -*-
import requests, time, sys, re, random, os, datetime
sys.path.append('c:/test_py/tool')
from get_html import HtmlPro
from proxy import Proxies, Mongo
from fake_useragent import UserAgent
from lxml import etree

class DownloadPic:
    def get_article_content(self, url):
        print(url)
        this_page_url = url
        proxies = pro.get_random_proxy()
        content = hp.get_html(this_page_url, proxies)
        html = etree.HTML(content)
        try:
            title = html.xpath('/html/head/title/text()')[0]
        except IndexError:
            title = this_page_url.split('/')[-1]
        save_path = 'C:/test_py/spiderTest/media_spider/tieba/%s%s' % (title,
                                                                       str(time.strftime('%m-%d', time.localtime())))
        self.make_dir(save_path) # 建立图片存放文件夹
        pic_list = self.get_pic_from_content(content) # 获取帖子里面的图片链接
        self.download_pic_from_pic_list(pic_list, save_path)

    def get_pic_from_content(self, html): # 获取帖子里面的图片
        html = html
        pic_list = re.findall(r' src="(https://imgsa\.baidu\.com/forum/.*?)" ', html)
        print('获取到%s张表情' % str(len(pic_list)))
        return pic_list

    def download_pic_from_pic_list(self, pic_list, save_path): # 下载帖子里面的图片
        for pic in pic_list:
            while True:
                try:
                    pic_content = requests.get(pic).content
                    break
                except Exception as e:
                    print(e.args)
            self.save_pic_from_download(pic_content, save_path, pic.split('.')[-1])
            time.sleep(random.uniform(0, 1))

    def save_pic_from_download(self, pic_content, save_path, save_type):
        # 查看保存的文件夹已存在的图片数量
        pic_count = len(os.listdir(save_path))
        pic_name = str(pic_count + 1) + '.' + save_type
        save_path_final =  save_path + os.path.sep + pic_name
        print(save_path_final)
        try:
            with open(save_path_final.encode('gbk'), 'wb') as fl:
                fl.write(pic_content)
                fl.close()
            print('保存一张表情')
        except OSError:
            print('获取失败')


    def make_dir(self, save_path): # 根据路径建立文件夹
        if os.path.exists(save_path.encode('gbk')):
            print('文件夹已存在')
        else:
            os.mkdir(save_path.encode('gbk'))
            print('文件夹已建立')

    def main(self, base_url):
        proxies = pro.get_random_proxy()
        content = hp.get_html(base_url, proxies)
        tiezi_id = base_url.split('/')[-1]
        total_page = re.findall('a href="/p/%s\?pn=(.*?)">尾页' % tiezi_id, content)[0]
        for page in range(1, int(total_page) + 1):
            url = base_url + '?pn=' + str(page)
            self.get_article_content(url)

if __name__ == '__main__':
    pro = Proxies()
    hp = HtmlPro()
    dp = DownloadPic()
    dp.main('https://tieba.baidu.com/p/4483188125')