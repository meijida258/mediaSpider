# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from .items import ArtistItem, MusicItem, MusicCommentsItem, AlbumItem

class ScrapyCloudmusicPipeline(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.CloudMusic
        self.comments_collection = self.db.MusicComments
        self.music_collection = self.db.Musics
        self.artist_collection = self.db.Artists
        self.album_collection = self.db.Albums

    def process_item(self, item, spider):
        if isinstance(item, MusicItem):
            if not self.is_repeat(dict(item), self.music_collection):
                self.music_collection.insert(dict(item))
        elif isinstance(item, MusicCommentsItem):
            if not self.is_repeat(dict(item), self.comments_collection):
                self.comments_collection.insert(dict(item))
        elif isinstance(item, ArtistItem):
            if not self.is_repeat(dict(item), self.artist_collection):
                # self.artist_collection.insert(dict(item))
                print(dict(item))
        elif isinstance(item, AlbumItem):
            if not self.is_repeat(dict(item), self.album_collection):
                self.album_collection.insert(dict(item))
        return item

    def is_repeat(self, item, collection):
        if collection.find({'artist_id':item['artist_id']}).count() == 0:
            return False
        else:
            return True

if __name__ == '__main__':
    scp = ScrapyCloudmusicPipeline()
    # print(list(scp.artist_collection.aggregate(
    #     [
    #         {'$group':{'_id':'$artist_from_country', 'count':{'$sum':1}}}
    #     ]
    # )))