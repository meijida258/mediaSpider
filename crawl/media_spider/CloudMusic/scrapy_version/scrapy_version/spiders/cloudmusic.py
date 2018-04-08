import scrapy
import re
from scrapy.http import Request
from lxml import etree
from ..mongoconn import mongo

class CloudMusicSpider(scrapy.Spider):
    name = 'cloudmusic'

    def __init__(self):
        scrapy.Spider.__init__(self)


    def start_requests(self):
        url = 'https://music.163.com/m/artist?id=159300'
        request = Request(url=url, callback=self.parse)
        request.meta['PhantomJS'] = True
        yield request


    def parse(self, response):
        source_artist_music_list = response.xpath('//*[@id="artist-top50"]').extract()



