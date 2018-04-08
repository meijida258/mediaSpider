# -*- coding: utf-8 -*-
import scrapy, os

from scrapy.spider import Request
from ..items import MeizituItem

class Spider1Spider(scrapy.Spider):
    name = "spider_1"
    allowed_domains = ["mmjpg.com"]
    start_urls = ['http://www.mmjpg.com/']
    base_url = 'http://www.mmjpg.com/home/'
    base_path = 'C:/Users/Administrator/Desktop/fhx20161004/'

    def start_requests(self):
        for page in range(64, 65):
            url = self.base_url + str(page)
            yield Request(url, callback=self.parse_pic_set_url)

    def parse_pic_set_url(self, response):
        result = response.xpath('/html/body/div[2]/div[1]/ul/li')
        items = []
        for li in result:
            item = MeizituItem()
            item['pic_set_url'] = li.xpath('span/a/@href').extract()[0]
            item['pic_title'] = li.xpath('span/a/text()').extract()[0]
            items.append(item)
        for item in items:
            if not os.path.exists(self.base_path + item['pic_title']):
                os.mkdir(self.base_path + item['pic_title'])
            if len(os.listdir(self.base_path + item['pic_title'])) == 0:
                yield Request(item['pic_set_url'], meta={'item_pic_set': item}, callback=self.parse_pic_list)
            else:
                pass
    def parse_pic_list(self, response):
        item_2 = response.meta['item_pic_set']
        pic_count = response.xpath('//*[@id="page"]/a[7]/text()').extract()[0]
        # 分割出一个基本的图片url
        base_pic_url = '/'.join(str(response.xpath('//*[@id="content"]/a/img/@src').extract()[0]).split('/')[:-1])
        # 获取图片格式
        pic_type = str(response.xpath('//*[@id="content"]/a/img/@src').extract()[0]).split('.')[-1]
        for i in range(1, int(pic_count) + 1):
            item = MeizituItem()
            item['pic_title'] = item_2['pic_title']
            item['pic_set_url'] = item_2['pic_set_url']
            item['pic_url'] = base_pic_url + '/' + str(i) + '.' + pic_type
            item['pic_save_path'] = self.base_path + item['pic_title'] +'/' + str(i) + '.' + pic_type
            yield item

