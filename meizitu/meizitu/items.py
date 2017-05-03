# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeizituItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pic_set_url = scrapy.Field() # 合集地址
    pic_url = scrapy.Field() # 图片地址
    pic_title = scrapy.Field() # 合集名称
    pic_save_path = scrapy.Field()
