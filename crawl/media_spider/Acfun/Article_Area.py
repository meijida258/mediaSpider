# -*- coding: UTF-8 -*-
import requests, time, random, sys, jieba.analyse
sys.path.append('c:/test_py/tool')
from lxml import etree
from pymongo import MongoClient
from Mongo_pro import Mongo
from get_html import HtmlPro
from wordcloud import WordCloud, STOPWORDS
from fake_useragent import UserAgent
import matplotlib.pyplot as plt

class ArticleGet:
    def __init__(self):
        self.article_url_header = 'http://www.acfun.cn/v/list73/index_'
        self.article_url_end = '.htm'
        self.article_type = '工作·情感'

        self.client = MongoClient('localhost', 27017)
        self.db = self.client.AcfunArticle
        self.collection = self.db.Article

    def get_page_html(self, page):
        time.sleep(random.uniform(0.5, 2))
        url = self.article_url_header + str(page) + self.article_url_end
        print ('获取:' + url)
        target_html = hp.get_html(url)
        self.get_article_info(target_html)
        new_page = page + 1
        self.get_page_html(new_page)

    def get_article_info(self, target_html):
        html = etree.HTML(target_html)
        for article_item in html.xpath('//*[@id="block-content-article"]/div[2]/div')[:-1]:
            page_article_info = {}
            page_article_info['article_read'] = article_item.xpath('p/span[2]/text()')[0]
            page_article_info['article_answer'] = article_item.xpath('p/span[1]/text()')[0]
            page_article_info['url_address'] = 'http://www.acfun.cn' + article_item.xpath('a[1]/@href')[0]
            page_article_info['article_title'] = article_item.xpath('a[2]/text()')[0]
            page_article_info['article_release'] = article_item.xpath('a[2]/@title')[0][4:]
            page_article_info['article_user'] = article_item.xpath('p/a/text()')[0]
            page_article_info['article_desc'] = article_item.xpath('div/text()')[0]
            page_article_info['article_type'] = self.article_type
            if self.collection.find({'article_title':page_article_info['article_title']}).count() == 0:
                self.insert_article_info(page_article_info)
            else:
                print ('获取到重复的文章，重复文章题目为：')
                print (page_article_info['article_title'])
                print ('查询作者是否一样')
                exist_articles = self.collection.find({'article_title':page_article_info['article_title']})
                for exist_article in exist_articles:
                    if page_article_info['article_user'] == exist_article['article_user']:
                        print ('查询到相同作者')
                        print ('程序结束')
                        exit()

    def insert_article_info(self, page_article_info):
        mon.insert_dict(page_article_info, 'article_title', self.collection)

    def main_controller(self):
        start_page = 1
        self.get_page_html(start_page)

    def get_random_article(self):
        article_lists = self.collection.find()
        result = []
        while True:
            random_index = random.randint(0, 19)
            pick_article_lists = article_lists[int(article_lists.count() / 20) * random_index :(int(article_lists.count() / 20) * random_index + int(article_lists.count() / 20))]
            for article in pick_article_lists:
                if int(article['article_answer']) > 150:
                    result.append(article)
            if len(result) > 0:
                return result[random.randint(0, len(result) - 1)]
            else:
                print ('未找到合适文章，开始重新搜索')

    def get_article_content(self):
        result = self.get_random_article()
        html = etree.HTML(hp.get_html(result['url_address']))
        content = ''
        content += ('title:' + result['article_title'])
        content += '\n'
        content += ('release:' + result['article_release'])
        content += '\n'
        content += ('user:' + result['article_user'])
        content += '\n'
        content += 'content:'
        for each_p in html.xpath('//*[@id="area-player"]/p/text()'):
            content += each_p.strip()
            content += '\n'
        content += result['url_address']
        return content
class ArticleAnalysis:
    def title_analysis(self):
        titles = ''
        for article_info in art_get.collection.find():
            titles = titles + '|' + article_info['article_title']
        result = jieba.analyse.extract_tags(titles, topK=102, withWeight=True, allowPOS=())

        return result

    def drawWordCloud(self, result):
        wordcloud = WordCloud(background_color='white', max_font_size=100, relative_scaling=.2).fit_words(result)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()

    def get_word_cloud(self):
        # 获取所有的标题并处理
        result = self.title_analysis()
        # 绘制词云
        self.drawWordCloud(result)

if __name__ == '__main__':
    hp = HtmlPro()
    mon = Mongo()
    art_get = ArticleGet()
    art_aly = ArticleAnalysis()
    print (art_get.get_article_content())
    # art_get.main_controller() # 获取文章
    # art_aly.get_word_cloud() # 绘制词云图