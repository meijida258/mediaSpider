# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyVersionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ArtistMusicItem(scrapy.Item):
    music_id = scrapy.Field()
    artist_id = scrapy.Field()

class MusicItem(scrapy.Item):
    music_name = scrapy.Field()
    music_id = scrapy.Field()
    music_author_name = scrapy.Field()
    music_author_id = scrapy.Field()
    music_lyric = scrapy.Field()
    music_comments_count = scrapy.Field()
    music_hot_comments = scrapy.Field()
    music_mv_id = scrapy.Field()