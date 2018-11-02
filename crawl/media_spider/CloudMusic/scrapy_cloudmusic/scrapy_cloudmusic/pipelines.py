# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
# from .items import ArtistItem, MusicItem, MusicCommentsItem, AlbumItem

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
            if self.music_collection.find({'music_id': item['music_id']}).count() == 0:
                self.music_collection.insert(dict(item))
        elif isinstance(item, MusicCommentsItem):
            if self.comments_collection.find({'music_id': item['music_id']}).count() == 0:
                self.comments_collection.insert(dict(item))
        elif isinstance(item, ArtistItem):
            if self.artist_collection.find({'artist_id': item['artist_id']}).count() == 0:
                self.artist_collection.insert(dict(item))
        elif isinstance(item, AlbumItem):
            if self.album_collection.find({'album_id': item['album_id']}).count() == 0:
                self.album_collection.insert(dict(item))
        return item

if __name__ == '__main__':
    scp = ScrapyCloudmusicPipeline()
    print(scp.artist_collection.find({'artist_from_country':'其他女歌手'}).count())
