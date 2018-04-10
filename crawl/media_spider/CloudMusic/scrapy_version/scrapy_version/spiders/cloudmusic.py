import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.http import Request
from ..redis import conn_reds

from ..items import ArtistMusicItem

class CloudMusicSpider(scrapy.Spider):
    name = 'cloudmusic'
    redis_key = 'cloudmusic:start_urls'
    allowed_domains = ['http://music.163.com/']

    rules = (
        Rule(LinkExtractor(), callback='parse', follow=True),
    )

    # def __init__(self):
    #     scrapy.Spider.__init__(self)
    #     self.reds = conn_reds.get_redis_conn(2)
    #     self.artist_base_url = 'https://music.163.com/m/artist?id={}'

    # def start_requests(self):
    #     if self.reds.scard('wait_visit_music') == 1:
    #         print('111111111111111111111')
    #         artist_dict = mongo.artist_collection.find_one({'crawl_type':0})
    #         mongo.artist_collection.update({'id': artist_dict['artist_id']},
    #                                        {'$set': {'crawl_type': 1}})
    #         temp_artist_dict = self.reds.srandmember('wait_visit_music')
    #         mongo.artist_collection.update({'id':json.loads(temp_artist_dict)['artist_id']},
    #                                        {'$set':{'crawl_type':2}})
    #         url = self.artist_base_url.format(artist_dict['id'])
    #         request = Request(url=url, callback=self.parse)
    #         request.meta['firefox'] = True
    #         yield request
    #     elif self.reds.scard('wait_visit_music') == 0:
    #         print('2222222222222222')
    #         artist_dict = mongo.artist_collection.find_one({'crawl_type': 0})
    #         url = self.artist_base_url.format(artist_dict['id'])
    #         request = Request(url=url, callback=self.parse)
    #         request.meta['firefox'] = True
    #         yield request
    #     else:
    #         temp_artist_dict = self.reds.srandmember('wait_visit_music')
    #         music_url = 'http://music.163.com/#/song?id={}'.format(json.loads(self._unicode(temp_artist_dict))['music_id'])
    #         yield Request(url=music_url, callback=self.parse_music_page)

    # def start_requests(self):
    #     url = 'http://music.163.com/#/artist?id=159300'
    #     request = Request(url=url, callback=self.parse)
    #     request.meta['firefox'] = True
    #     yield request

    def parse(self, response):
        source_artist_music_list = response.xpath('//*[@id="artist-top50"]/div[2]/div[1]/div[1]/div[1]/table/tbody/tr').extract()
        for each_tr in source_artist_music_list:
            song_id = re.findall(r'href="/song\?id=(\d+)"', each_tr)
            try:
                print(song_id[0])
            except:
                pass

    def parse_music_page(self, response):
        print('11111111111111111111111111111111111111111')
        print(response.url)
        yield


    def _unicode(self, s):
        if isinstance(s, str):
            try:
                return s.decode('utf-8')
            except:
                return s