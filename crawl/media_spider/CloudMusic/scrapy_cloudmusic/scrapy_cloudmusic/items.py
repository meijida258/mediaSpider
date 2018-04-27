# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyCloudmusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MusicItem(scrapy.Item):
    music_total_comment = scrapy.Field()
    hot_comments = scrapy.Field()
    music_id = scrapy.Field()