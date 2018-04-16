# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyCloudmusicPipeline(object):

    def write_result(self, data):
        with open('result.txt', 'a') as fl:
            fl.write(data)
    def process_item(self, item, spider):
        self.write_result(item['music_total_comment'])
        return item
