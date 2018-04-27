# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class ScrapyCloudmusicPipeline(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.CloudMusic
        self.comments_collection = self.db.MusicComments


    def process_item(self, item, spider):
        if not self.is_repeat(dict(item), self.comments_collection):
            self.comments_collection.insert(dict(item))
        return item

    def is_repeat(self, item, collection):
        if collection.find(item).count() == 0:
            return False
        else:
            return True