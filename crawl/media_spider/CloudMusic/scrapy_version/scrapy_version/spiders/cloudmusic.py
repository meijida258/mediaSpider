import scrapy
import re
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from lxml import etree
from ..mongoconn import mongo
from ..redis import conn_reds

class CloudMusicSpider(RedisSpider):
    name = 'cloudmusic'
    redis_key = 'cloudmusic:start_urls'

    def __init__(self):
        scrapy.Spider.__init__(self)
        #self.reds = conn_reds.get_redis_conn(2)

    def start_requests(self):
        url = 'https://music.163.com/m/artist?id=159300'
        request = Request(url=url, callback=self.parse)
        request.meta['firefox'] = True
        yield request


    def parse(self, response):
        source_artist_music_list = response.xpath('//*[@id="artist-top50"]/div[2]/div[1]/div[1]/div[1]/table/tbody/tr').extract()
        for each_tr in source_artist_music_list:
            song_id = re.findall(r'href="/song\?id=(\d+)"', each_tr)
            #self.reds.set(song_id)



