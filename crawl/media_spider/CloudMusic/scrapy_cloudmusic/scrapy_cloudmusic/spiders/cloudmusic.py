# 通过所有

from scrapy import spiders, Request, FormRequest
import re, json
from ..comment_params_get import pg
from ..items import MusicItem

class CloudMusic(spiders.Spider):
    name = 'cloudmusic'
    # start_urls = ['http://music.163.com/#/discover/artist/cat?id={}&initial={}']
    artists_base_url = 'http://music.163.com/#/discover/artist/cat?id=1001&initial={}'
    artist_base_url = 'http://music.163.com/#/artist?id={}'
    music_base_url = 'http://music.163.com/#/song?id={}'
    artist_country_ids = {u'华语男歌手': 1001, u'华语女歌手': 1002, u'华语组合/乐队': 1003,
                               u'欧美男歌手': 2001, u'欧美女歌手': 2002, u'欧美组合/乐队': 2003,
                               u'日本男歌手': 6001, u'日本女歌手': 6002, u'日本组合/乐队': 6003,
                               u'韩国男歌手': 7001, u'韩国女歌手': 7002, u'韩国组合/乐队': 7003,
                               u'其他男歌手': 4001, u'其他女歌手': 4002, u'其他组合/乐队': 4003}

    initial_num = list(range(65, 68))
    initial_num.append(0)

    def start_requests(self):
        for initial in self.initial_num:
            url = self.artists_base_url.format( initial)
            request = Request(url=url, callback=self.parse_artists_id, dont_filter=True)
            request.meta['firefox'] = True
            yield request

    def parse_artists_id(self, response):
        hot_artists = re.findall(r'<a title="(.*?)的音乐" href="/artist\?id=(\d+)" class="msk"></a>', response.text)
        other_artists = re.findall(r'<a href="/artist\?id=(\d+)" class="nm nm-icn f-thide s-fc0" title=".*?的音乐">(.*?)</a>', response.text)
        for artist in hot_artists:
            url = self.artist_base_url.format(artist[1])
            request = Request(url=url, callback=self.parse_music_id)
            request.meta['firefox'] = True
            yield request
        for artist in other_artists:
            url = self.artist_base_url.format(artist[0])
            request = Request(url=url, callback=self.parse_music_id)
            request.meta['firefox'] = True
            yield request

    def parse_music_id(self, response):
        source_artist_music_list = response.xpath(
            '//*[@id="artist-top50"]/div[2]/div[1]/div[1]/div[1]/table/tbody/tr').extract()
        for each_tr in source_artist_music_list:
            song_id = re.findall(r'href="/song\?id=(\d+)"', each_tr)
            params = pg.get_params_data()
            yield FormRequest(url=self.music_base_url.format(song_id), formdata=params, callback=self.get_music_comment)



    def get_music_comment(self, response):
        result = json.loads(response.body_as_unicode())
        item = MusicItem()
        item['music_total_comment'] = result['total']
        yield item
