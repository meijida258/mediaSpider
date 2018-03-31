# -*- coding: UTF-8 -*-
import requests, time, sys, re, random
sys.path.append('c:/mediaSpider/tool')
from lxml import etree
from pymongo import MongoClient
from GetHtml import hp
from ProxyMantenance import prou
from fake_useragent import UserAgent
from Crypto.Cipher import AES
from multiprocessing.dummy import Pool as ThreadingPool
import base64, json

class Comments:
    def __init__(self):
        self.headers={'Cookie':'appver=1.5.0.75771',
                      'Referer':'http://music.163.com/',
                      'User-Agent':ua.random}

        self.first_param_comment = "{rid:\"\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
        self.first_param_lyric = '{id: \"music_id\", lv: \"-1\", tv: \"-1\", csrf_token: \"\"}'
        self.second_param = '010001'
        self.third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.forth_param = '0CoJUm6Qyw8W8jud'

    def get_params(self, first_param, music_id=None):
        iv = '0102030405060708'
        first_key = self.forth_param
        second_key = 'F' * 16
        deal_first_param = first_param.replace('music_id', str(music_id))
        h_encText = self.AES_encrypt(deal_first_param, first_key, iv).decode('utf-8')
        h_encText = self.AES_encrypt(h_encText, second_key, iv).decode('utf-8')
        return h_encText

    def get_encSecKey(self):
        encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
        return encSecKey

    def AES_encrypt(self, text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    def get_comment(self, music_id, proxies=None):
        music_comment_url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token=' % str(music_id)
        params_data = {}
        params_data['params'] = self.get_params(self.first_param_comment)
        params_data['encSecKey'] = self.get_encSecKey()
        used_proxies = proxies
        while True:
            try:
                time.sleep(random.uniform(0, 2))
                print ('获取id为：%s的评论' % music_id)
                post_response = requests.post(music_comment_url, headers=self.headers, data=params_data, proxies=used_proxies,
                                              timeout=10).content
                break
            except Exception:
                used_proxies = prou.get_random_proxy('http')
        try:
            json_dict = json.loads(post_response.decode('utf-8'))
        except ValueError:
            json_dict = json.loads("""{"isMusician":false,"userId":-1,"topComments":[],"hotComments":[],"comments":[],"total":0}""")
        return json_dict

    def make_comment_dict(self, json_dict, music_dict):
        new_music_dict = music_dict
        try:
            new_music_dict['total_comment'] = json_dict['total']
        except:
            return new_music_dict
        hot_comment_count = 1
        for each_comment in json_dict['hotComments']:
            print ('获取第%s条评论' % hot_comment_count)
            new_music_dict['hotComment_%s' % hot_comment_count] = each_comment['user']['nickname'] + u'|' + str(each_comment['likedCount']) + u'|' + each_comment['content']
            hot_comment_count += 1
        return new_music_dict

    def get_lyric(self, music_id, proxies=None):
        music_comment_url = 'http://music.163.com/weapi/song/lyric?csrf_token='
        params_data = {}
        params_data['params'] = self.get_params(self.first_param_lyric, music_id)
        params_data['encSecKey'] = self.get_encSecKey()
        used_proxies = proxies
        while True:
            try:
                time.sleep(random.uniform(0, 2))
                print ('获取id为：%s的歌词' % music_id)
                post_response = requests.post(music_comment_url, headers=self.headers, data=params_data, proxies=used_proxies,
                                              timeout=10).content
                break
            except Exception:
                print('获取id为：%s的歌词遇到错误' % music_id)
                if used_proxies:
                    print('使用的代理为%s' % str(used_proxies['http']))
                used_proxies = prou.get_random_proxy('http')
        try:
            json_dict = json.loads(post_response.decode('utf-8'))
        except ValueError:
            json_dict = json.loads('{"lrc": {"lyric": "歌词获取出错"}}')
        if 'lrc' in json_dict:
            try:
                music_lyric = json_dict['lrc']['lyric']
            except KeyError:
                music_lyric = '歌词未收录'
            return music_lyric
        elif 'uncollected' in json_dict:
            music_lyric = '歌词未收录'
            return music_lyric
        elif 'nolyric' in json_dict:
            music_lyric = '纯音乐'
            return music_lyric

    def music_main(self, music_id, music_dict, proxies):

        new_music_dict = music_dict
        new_music_dict['lyric'] = self.get_lyric(music_id, proxies)
        comment_json = self.get_comment(music_id, proxies)
        new_music_dict = self.make_comment_dict(comment_json, new_music_dict)
        return new_music_dict

class Music:
    def __init__(self):
        self.music_basic_url = 'http://music.163.com/song'
        self.headers = {'Cookie':'appver=1.5.0.75771',
                      'Referer':'http://music.163.com/',
                      'User-Agent':ua.random}

        self.first_param_artist = '{categoryCode: \"5001\", offset: \"page_code\", total: \"false\", limit: \"60\", csrf_token: \"\"}'


    def get_music_sheet_tags(self, artist_id): # 获取artist_id的歌单字符串
        proxies = prou.get_random_proxy('http')
        while True:
            try:
                time.sleep(random.uniform(0, 2))
                print ('获取ID为%s的作者歌单' % str(artist_id))
                html = requests.get('http://music.163.com/artist', headers=self.headers, params={'id':artist_id},
                                    timeout=30, proxies=proxies).content
                music_tr_tags = re.findall(r'<textarea style="display:none;">(.*?)</textarea>', html.decode('utf-8'))[0]
                print ('获取完成')
                break
            except IndexError:
                print ('作者没有作品')
                # mgs.artist_collection.update({'id': str(artist_id)},
                #                              {'$set': {'store_type': 'Finished'}})
                return None
            except Exception as e:
                proxies = prou.get_random_proxy('http')
                print ('获取出错，重新获取')
                print (e)
        return music_tr_tags

    def get_music_dict_from_sheet(self, music_tr_tags): # 处理歌单字符串，从中获取所包含的artist的热门50首作品及相关信息
        temp = music_tr_tags.replace('null', "0")
        temp = temp.replace('false', '0')
        temp = temp[1:-1]
        print (temp)
        music_dict_list = []
        split_str = temp[:4]
        for each_json_str in temp.split(',' + split_str):
            if each_json_str.startswith('{'):
                print ('处理字符串')
                each_json = self.load_json_value_error(each_json_str)
                music_dict = self.get_music_json_info_from_sheet(each_json) # 从歌单获取歌曲的基本信息
                music_dict_list.append(music_dict) # 制作基本的字典并存入list用于爬取歌词评论
            else:
                print ('处理字符串')
                each_json_str = split_str + each_json_str
                each_json = self.load_json_value_error(each_json_str)
                music_dict = self.get_music_json_info_from_sheet(each_json)
                music_dict_list.append(music_dict) # 制作基本的字典并存入list用于爬取歌词评论
        return music_dict_list # 返回包含歌名、专辑等的字典list

    def load_json_value_error(self, json_str):

        temp_str = json_str
        while True:
            try:
                json_result = json.loads(temp_str)
                break
            except ValueError as e:
                print ('json出错')
                error_column = re.findall(r"char (.*?)\)", str(e.args))[0]
                print (error_column)
                temp_str = temp_str[:int(error_column) - 1] + ' ' + temp_str[int(error_column):]
                print ('删除导致错误的字符')
        return json_result
    def get_music_json_info_from_sheet(self, music_json):
        store_dict = {}
        store_dict['music'] = music_json['name']
        store_dict['music_id'] = music_json['id']
        store_dict['music_album'] = music_json['album']['name']
        store_dict['music_album_id'] = music_json['album']['id']
        try:
            store_dict['singer'] = music_json['artist'][0]['name']
            store_dict['singer_id'] = music_json['artist'][0]['id']
        except KeyError:
            print ('%s作者获取出错，可能有多个作者' % store_dict['music'].encode('utf-8'))
            try:
                for each_singer_dict in music_json['artists']:
                    if 'singer' in store_dict:
                        store_dict['singer'] = store_dict['singer'] + '|' + each_singer_dict['name']
                        store_dict['singer_id'] = store_dict['singer_id'] + '|' + str(each_singer_dict['id'])
                    else:
                        store_dict['singer'] = each_singer_dict['name']
                        store_dict['singer_id'] = str(each_singer_dict['id'])
                print ('共%s个作者，获取完成'% len(music_json['artists']))
            except KeyError:
                store_dict['singer'] = '未获取到'
                store_dict['singer_id'] = '未获取到'
                print ('未知原因，作者获取出错')
        store_dict['music_score'] = music_json['score']
        return store_dict

    def get_controller(self, music_dict):
        complete_music_dict = com.music_main(music_dict['music_id'], music_dict, prou.get_random_proxy('http'))

        print ('获取id为%s的歌曲完整信息及热评' % str(music_dict['music_id']))
        mgs.insert_dict(mgs.music_collection, complete_music_dict, 'music_id', music_dict['music_id'])
        singer_id = music_dict['singer_id']
        if music_dict['singer_id'].find('|') > 0:
            singer_id_list = singer_id.split('|')
            for each_singer_id in singer_id_list:
                self.update_singer_store_music(each_singer_id)
        else:
            self.update_singer_store_music(singer_id)

    def update_singer_store_music(self, singer_id):
        try:
            store_count = mgs.artist_collection.find({'id': singer_id})[0]['store_musics']
            store_count += 1
            mgs.artist_collection.update({'id':singer_id}, {'$set':{'store_musics':store_count}})
            print ('更新artist_collection中id为%s的记录信息' % str(singer_id))
        except IndexError:
            print ('无id为%s的作者' % str(singer_id))

    def thread_controller(self):
        artist_dict_list = mgs.artist_collection.find({'store_type':'Not Start', 'type':u'华语女歌手'})
        artist_count =  artist_dict_list.count()
        random_artist_count = random.randint(0, artist_count - 1)
        start_time = time.time()
        music_tr_tags = self.get_music_sheet_tags(artist_dict_list[random_artist_count]['id'])
        # music_tr_tags = self.get_music_sheet_tags(17750)
        if music_tr_tags:
            music_dict_list = self.get_music_dict_from_sheet(music_tr_tags)
            print ('%s的歌单获取完成，开始获取评论及歌词' % str(artist_dict_list[random_artist_count]['name'].encode('utf-8')))
            # for music_dict in music_dict_list:
            #     self.get_controller(music_dict)
            pool = ThreadingPool(4)
            pool.map(self.get_controller, music_dict_list)
            pool.close()
            pool.join()
            print ('%s的作品获取完成' % str(artist_dict_list[random_artist_count]['id']))
            mgs.artist_collection.update({'id':artist_dict_list[random_artist_count]['id']}, {'$set':{'store_type':'Finished'}})
        print('获取总共花费时间%s' % str(time.time() - start_time))
        self.thread_controller()

class Artist:
    def __init__(self):
        self.artist_country_ids = {u'华语男歌手':1001, u'华语女歌手':1002, u'华语组合/乐队':1003,
                                  u'欧美男歌手':2001, u'欧美女歌手':2002, u'欧美组合/乐队':2003,
                                  u'日本男歌手':6001, u'日本女歌手':6002, u'日本组合/乐队':6003,
                                  u'韩国男歌手':7001, u'韩国女歌手':7002, u'韩国组合/乐队':7003,
                                  u'其他男歌手':4001, u'其他女歌手':4002, u'其他组合/乐队':4003}

        self.name_start_ids = list(range(65, 91))
        self.name_start_ids.append(0)

    def main_controller(self):
        for artist_key in self.artist_country_ids.keys():
            artists_url = 'http://music.163.com/discover/artist/cat'
            for name_start_id in self.name_start_ids:
                artists_url_params_id = self.artist_country_ids[artist_key]
                artists_url_params_initial = name_start_id
                print ('获取%s-%s开头的作者名' % (artist_key.encode('utf-8') , str(chr(name_start_id))))
                proxies = prou.get_random_proxy('http')
                print ('使用代理：%s' % str(proxies))
                while True:
                    try:
                        time.sleep(random.uniform(1, 2))
                        html = requests.get(artists_url, proxies= proxies, headers=com.headers, timeout=30, params={'id':artists_url_params_id,
                        'initial':artists_url_params_initial}).content
                        break
                    except Exception:
                        proxies = prou.get_random_proxy('http')
                self.get_artist(html, artist_key)
                print ('html获取完成，开始获取html中的作者信息')

    def get_artist(self, html, artist_key):
        a_tags = re.findall(r'<a href="(.?)/artist\?id=(.*?)" class="nm nm-icn f-thide s-fc0" title="(.*?)">(.*?)</a>', html.decode('utf-8'))
        print ('获取到%s条作者信息' % str(len(a_tags)))
        for a_tag in a_tags:
            artist_dict = {}
            artist_dict['type'] = artist_key
            artist_dict['id'] = a_tag[1]
            artist_dict['name'] = a_tag[3]
            mgs.insert_dict(mgs.artist_collection, artist_dict, 'id', a_tag[1])


class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.music_db = self.client.Music
        self.music_collection = self.music_db.music_collection

        self.artist_db = self.client.Artist
        self.artist_collection = self.artist_db.artist_collection

    def insert_dict(self, save_collection,need_insert_dict, identify_key, identify_value):
        if save_collection.find({identify_key:identify_value}).count() == 0:
            save_collection.insert(need_insert_dict)
            print ('插入一条包含%s：%s的信息' %(identify_key, identify_value))
        else:
            print ('重复信息')

if __name__ == '__main__':
    mgs = MongoSet()
    ua = UserAgent()
    com = Comments()
    # hp = HtmlPro()
    mu = Music()
    art = Artist()
    mu.thread_controller()