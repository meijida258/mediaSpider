# 通过所有

from scrapy import spiders, Request, FormRequest
import re, json
from ..comment_params_get import pg
from ..items import MusicItem, MusicCommentsItem, ArtistItem
import random, itertools

class CloudMusic(spiders.Spider):
    name = 'cloudmusic'
    allowed_domains = ['music.163.com']
    artists_base_url = 'http://music.163.com/#/discover/artist/cat?id={}&initial={}'
    artist_base_url = 'http://music.163.com/#/artist?id={}'
    music_base_url = 'http://music.163.com/#/song?id={}'
    comment_base_url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='
    artist_country_ids = {u'华语组合/乐队': 1003}
    wait_crawl = {u'华语男歌手': 1001, u'华语女歌手': 1002, u'华语组合/乐队': 1003,
                  u'欧美男歌手': 2001, u'欧美女歌手': 2002, u'欧美组合/乐队': 2003,
                               u'日本男歌手': 6001, u'日本女歌手': 6002, u'日本组合/乐队': 6003,
                               u'韩国男歌手': 7001, u'韩国女歌手': 7002, u'韩国组合/乐队': 7003,
                               u'其他男歌手': 4001, u'其他女歌手': 4002, u'其他组合/乐队': 4003}

    download_delay = random.uniform(1, 3) # 下载间隔

    initial_nums = list(range(65, 91))
    initial_nums.append(0)

    # artists_page_params = ((country_id, initial_num) for country_id in artist_country_ids.values()
    #                                                 for initial_num in initial_nums) # 国籍id与首字母num生成所有组合
    artists_page_params = itertools.product(artist_country_ids.values(), initial_nums)

    # comment_params不随歌曲id变化，用类属性来保存
    comments_params = pg.get_params_data()

    def start_requests(self):
        for artists_page_param in self.artists_page_params:
            # 通过国籍id和首字母组合url
            url = self.artists_base_url.format(artists_page_param[0], artists_page_param[1])

            # dont_filter不过滤重复
            request = Request(url=url, callback=self.parse_artists_id, dont_filter=True)
            request.meta['firefox'] = True
            # 将国籍id保存到request.meta中，给callback=self.parse_artists_id使用
            request.meta['from_country_ind'] = artists_page_param[0]
            yield request

    def parse_artists_id(self, response):
        # 找到所有歌手id、名字->(id, name)
        artists = re.findall(r'<a href="\s*/artist\?id=(\d+)" class="nm nm-icn f-thide s-fc0" title=".*?的音乐">(.*?)</a>', response.text)
        for artist in artists:
            # 实例歌手item，保存数据
            artist_item = ArtistItem()
            artist_item['artist_name'] = artist[1]
            artist_item['artist_id'] = artist[0]
            artist_item['artist_from_country'] = list(self.artist_country_ids.keys())[list(self.artist_country_ids.values()).index(response.meta['from_country_ind'])]
            yield artist_item
            # 用url组装request
            url = self.artist_base_url.format(artist[0]) # 用id组合url
            request = Request(url=url, callback=self.parse_music_id, dont_filter=True)
            request.meta['firefox'] = True
            request.meta['artist_id'] = artist[0]
            yield request

    def parse_music_id(self, response):
        source_artist_music_list = response.xpath(
            '//*[@id="artist-top50"]/div[2]/div[1]/div[1]/div[1]/table/tbody/tr')
        for each_tr in source_artist_music_list:
            # 实例歌曲item，保存数据
            music_item = MusicItem()
            music_item['artist_id'] = response.meta['artist_id']
            music_id_url = each_tr.xpath('.//span[@class="txt"]/a/@href').extract_first()
            music_id = music_id_url.split('=')[-1]
            music_item['music_id'] = music_id
            music_item['music_title'] = each_tr.xpath('.//span[@class="txt"]/a/b/@title').extract_first()
            music_item['music_duration'] = each_tr.xpath('.//span[@class="u-dur "]/text()').extract_first()
            music_item['music_album_title'] = each_tr.xpath('.//div[@class="text"]/a/@title').extract_first()
            music_album_id_url = each_tr.xpath('.//div[@class="text"]/a/@href').extract_first()
            try:
                music_item['music_album_id'] = music_album_id_url.split('=')[-1]
            except:
                music_item['music_album_id'] = None
            yield music_item
            # 用url组装request
            # form_request = FormRequest(url=self.comment_base_url.format(music_id), formdata=self.comments_params,
            #                   callback=self.get_music_comment, dont_filter=True)
            # form_request.meta['music_id'] = music_id
            # yield form_request



    def get_music_comment(self, response):
        result = json.loads(response.text)
        item = MusicCommentsItem()
        item['total_comments'] = result['total']
        hot_comments = []
        try:
            hot_comments_ = result['hotComments']
            for comment in hot_comments_:
                hot_comments.append('|'.join([comment['user']['nickname'], comment['likedCount'], comment['content']]))
        except:
            pass
        item['hot_comments'] = hot_comments
        item['music_id'] = response.meta['music_id']
        yield item
