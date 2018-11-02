# 通过所有

from scrapy import spiders, Request
import re, json
from ..items import MusicItem, MusicCommentsItem, ArtistItem, AlbumItem
import random, itertools

class CloudMusic(spiders.Spider):
    name = 'cloudmusic'
    allowed_domains = ['music.163.com']
    artists_base_url = 'http://music.163.com/#/discover/artist/cat?id={}&initial={}'
    artist_country_ids = {u'韩国女歌手': 7002,u'其他男歌手': 4001, u'其他女歌手': 4002, u'其他组合/乐队': 4003}
    wait_crawl = {u'华语男歌手': 1001, u'华语女歌手': 1002, u'华语组合/乐队': 1003,
                  u'欧美男歌手': 2001, u'欧美女歌手': 2002, u'欧美组合/乐队': 2003,
                               u'日本男歌手': 6001, u'日本女歌手': 6002, u'日本组合/乐队': 6003,
                               u'韩国男歌手': 7001, u'韩国女歌手': 7002, u'韩国组合/乐队': 7003,
                               u'其他男歌手': 4001, u'其他女歌手': 4002, u'其他组合/乐队': 4003}

    download_delay = random.uniform(0.1, 0.3) # 下载间隔/

    initial_nums = list(range(65, 91))
    initial_nums.append(0)

    artists_page_params = itertools.product(artist_country_ids.values(), initial_nums)


    def start_requests(self): # 通过歌手页获取歌手信息
        for artists_page_param in self.artists_page_params:
            # 通过国籍id和首字母组合url
            url = self.artists_base_url.format(artists_page_param[0], artists_page_param[1])

            # dont_filter不过滤重复
            request = Request(url=url, callback=self.parse_artists_id, dont_filter=True)
            request.meta['firefox'] = True
            # 将国籍id保存到request.meta中，给callback=self.parse_artists_id使用
            request.meta['from_country_ind'] = artists_page_param[0]
            yield request

    def parse_artists_id(self, response):# 找到所有歌手id、名字->(id, name)
        artists = re.findall(r'<a href="\s*/artist\?id=(\d+)" class="nm nm-icn f-thide s-fc0" title=".*?的音乐">(.*?)</a>', response.text)
        for artist in artists:
            # 实例歌手item，保存数据
            artist_item = ArtistItem()
            artist_item['artist_name'] = artist[1]
            artist_item['artist_id'] = artist[0]
            artist_item['artist_from_country'] = list(self.artist_country_ids.keys())[list(self.artist_country_ids.values()).index(response.meta['from_country_ind'])]
            yield artist_item
            # 用url组装request
            url = 'http://music.163.com/api/artist/albums/{}?offset=0&limit=50'.format(artist[0]) # 用id组合url
            request = Request(url=url, callback=self.parse_album_id, dont_filter=True)
            request.meta['artist_id'] = artist[0]
            request.meta['json_result'] = True
            yield request

    def parse_album_id(self, response): # 通过artist_id获得歌手的专辑
        response_json = json.loads(response.body_as_unicode())
        album_item = AlbumItem()
        for album in response_json['hotAlbums']:
            album_item['artist_id'] = response.meta['artist_id']
            album_item['album_title'] = album['name']
            album_item['album_id'] = album['id']
            album_item['album_size'] = album['size']
            yield album_item
            url = 'http://music.163.com/api/album/{}'.format(album_item['album_id'])
            request = Request(url=url, callback=self.parse_music_id, dont_filter=True)
            request.meta['artist_id'] = album_item['artist_id']
            request.meta['json_result'] = True
            yield request

    def parse_music_id(self, response): # 通过album_id获得歌手专辑下的所有歌
        response_json = json.loads(response.body_as_unicode())
        for music in response_json['album']['songs']:
            # 实例歌曲item，保存数据
            music_item = MusicItem()
            music_item['artist_id'] = '/'.join([str(artist['id']) for artist in music['artists']]) # 多个作者保存列表
            music_item['music_id'] = music['id']
            music_item['music_title'] = music['name']
            music_item['music_popularity'] = music['popularity']
            music_item['music_duration'] = music['duration']
            music_item['music_mp3Url'] = music['mp3Url']
            music_item['music_album_title'] = response_json['album']['name']
            music_item['music_album_id'] = response_json['album']['id']
            yield music_item
            # 用url组装request
            if music_item['music_popularity'] > 15:
                request = Request(url='http://music.163.com/api/v1/resource/comments/R_SO_4_{0}/?rid=R_SO_4_{0}&offset=0&total=false&limit=10'.format(music['id']),
                                           callback=self.get_music_comment, dont_filter=True)
                request.meta['music_id'] = music['id']
                request.meta['artist_id'] = response.meta['artist_id']
                yield request



    def get_music_comment(self, response): # 通过music_id获取评论，默认获取热评，没有热评获取评论
        result = json.loads(response.body_as_unicode())
        item = MusicCommentsItem()
        item['total_comments'] = result['total']
        comments = list()
        if result['hotComments']:
            for comment in result['hotComments']:
                comments.append('|'.join([comment['user']['nickname'], str(comment['likedCount']), comment['content']]))
        else:
            for comment in result['comments']:
                comments.append('|'.join([comment['user']['nickname'], str(comment['likedCount']), comment['content']]))
        item['music_comments'] = comments
        item['music_id'] = response.meta['music_id']
        item['artist_id'] = response.meta['artist_id']
        yield item
