# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from .redis import conn_reds
import json

class ScrapyVersionPipeline(object):

    # def __init__(self):
    #     self.reds = conn_reds.get_redis_conn(2)

    def process_item(self, item, spider):
        save_json = {}
        save_json['music_id'] = item['music_id']
        save_json['artist_id'] = item['artist_id']
        #self.reds.sadd('wait_visit_music', json.dumps(save_json))
        return item
