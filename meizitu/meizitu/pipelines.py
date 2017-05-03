# -*- coding: utf-8 -*-
import requests, time
from .mongo import MongoSet
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MeizituPipeline(object):
    def process_item(self, item, spider):

        pic_url = item['pic_url']
        pic_save_path = item['pic_save_path']
        while True:
            try:
                pic_content = requests.get(pic_url, timeout=60).content
                break
            except Exception as e:
                print(e)
        time.sleep(2)
        with open(pic_save_path, 'wb') as pic:
            pic.write(pic_content)
        pic.close()
        # 存入数据库
        ms = MongoSet()
        ms.insert('pic_url', dict(item))
        return item
