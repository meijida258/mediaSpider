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

class MusicCommentsItem(scrapy.Item):
    total_comments = scrapy.Field()
    music_comments = scrapy.Field()
    music_id = scrapy.Field()
    artist_id = scrapy.Field()

class MusicItem(scrapy.Item):
    artist_id = scrapy.Field()
    music_id = scrapy.Field()
    music_title = scrapy.Field()
    music_album_id = scrapy.Field()
    music_album_title = scrapy.Field()
    music_duration = scrapy.Field()
    music_popularity = scrapy.Field()
    music_mp3Url = scrapy.Field()

class ArtistItem(scrapy.Item):
    artist_name = scrapy.Field()
    artist_id = scrapy.Field()
    artist_from_country = scrapy.Field()

class AlbumItem(scrapy.Item):
    artist_id = scrapy.Field()
    album_id = scrapy.Field()
    album_title = scrapy.Field()
    album_size = scrapy.Field()