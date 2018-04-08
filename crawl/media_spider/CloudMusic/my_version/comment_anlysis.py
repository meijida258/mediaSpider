# -*- coding: UTF-8 -*-
from pymongo import MongoClient
import jieba.analyse, wordcloud, time, xlwt
from fake_useragent import UserAgent
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import numpy as np

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Music
        self.collection = self.db.music_collection
        self.laji_collection = self.db.music_collcection

        self.client = MongoClient('localhost', 27017)
        self.db_2 = self.client.Artist
        self.collection_artist = self.db_2.artist_collection

    def pick_out_data_by_comment(self, comment_limit):
        data = self.collection.find()
        pick_data = []
        for each_message in data:
            if each_message['total_comment'] > comment_limit:
                pick_data.append(each_message)
        return sorted(pick_data, key=lambda x:x['total_comment'],reverse=True)

    def pick_out_data_by_author(self, singer_id):
        data = self.collection.find({'singer_id':singer_id})
        result = []
        for each_music in data:
            hot_comments = []
            count = 1
            while True:
                try:
                    hot_comments.append(each_music['hotComment_%s' % str(count)])
                    count += 1
                except KeyError:
                    print('歌曲%s无更多热门评论' % each_music['music'])
                    break
            if len(hot_comments) > 0:
                result.append(hot_comments)
        return result

class Analysis:
    def get_hot_comment(self, message):
        comment_count = 1
        comments_list = []
        message_info_dict = {}
        message_info_dict['music_name'] = message['music']
        message_info_dict['music_id'] = message['music_id']
        message_info_dict['music_singer'] = message['singer']
        message_info_dict['music_comment_count'] = message['total_comment']
        comments_list.append(message_info_dict)
        while True:
            try:
                comment = {}
                comment_list = message['hotComment%s' % str(comment_count)].split('|')
                comment['comment_name'] = comment_list[0]
                comment['comment_agree_count'] = comment_list[1]
                comment['comment'] = comment_list[2]
                comments_list.append(comment)
                comment_count += 1
            except KeyError:
                print('总共%s条热评' % str(comment_count))
                break
        return comments_list

    def tags_analysis(self, result_tags):
        jieba.analyse.set_stop_words('C:/test_py/tool/wordclound_stopword.txt')
        result = jieba.analyse.extract_tags(result_tags, topK=100, withWeight=True, allowPOS=())
        return result

    def drawWordCloud(self, result, background_pic, save_name=None):
        alice_mask = np.array(Image.open(background_pic))
        wordcloud = WordCloud(background_color='white', max_font_size=100, relative_scaling=.2,
                              font_path='C:/Python35/msyh.ttf',
                              mask=alice_mask).fit_words(result)
        if save_name:
            save_path = 'C:/test_py/spiderTest/media_spider/CloudMusic/%s.jpg' % save_name
            wordcloud.to_file(save_path)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()


    def write_excel(self, comment_limit):
        pick_data = mon.pick_out_data_by_comment(comment_limit)
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet1')
        row, column = 1, 0
        sheet.write(0, 0, 'artist')
        sheet.write(0, 1, 'music')
        sheet.write(0, 2, 'total_comment')
        sheet.write(0, 3, 'url')
        for each_data in pick_data:
            try:
                sheet.write(row, column, each_data['singer'].encode('gbk'))
            except Exception as e:
                sheet.write(row, column, each_data['singer'])
            try:
                sheet.write(row, column + 1, each_data['music'].encode('gbk'))
            except Exception as e:
                sheet.write(row, column + 1, each_data['music'])
            sheet.write(row, column + 2, each_data['total_comment'])
            sheet.write(row, column + 3, 'http://music.163.com/#/song?id=' + str(each_data['music_id']))
            row += 1
        wbk.save('C:/Users/Administrator/Desktop/评论大于1000的作品.xls'.encode('gbk'))

    def made_figure(self, comment_limit): # 获取评论数大于 1000 的歌曲，选取其中出现次数最多的歌手
        pick_data = mon.pick_out_data_by_comment(comment_limit)
        artist_music_dict = {}
        for each_data in pick_data:
            if each_data['singer'].find('|') > 0:
                author_list = each_data['singer'].split('|')
                for author in author_list:
                    if author in artist_music_dict:
                        artist_music_dict[author] = artist_music_dict[author] + 1
                    else:
                        artist_music_dict[author] = 1
            else:
                if each_data['singer'] in artist_music_dict:
                    artist_music_dict[each_data['singer']] = artist_music_dict[each_data['singer']] + 1
                else:
                    artist_music_dict[each_data['singer']] = 1
        result = []
        for key in artist_music_dict.keys():
            result.append((key, artist_music_dict[key]))

        return sorted(result, key=lambda x:x[1], reverse=True)
    def comment_analysis(self, author_id): # 根据作者id画出作者热门歌曲评论的词云图，调整参数有 1-背景模板图 2-保存名字
        data = mon.pick_out_data_by_author(author_id)
        comment = ''
        for each_comment_list in data:
            for each_comment in each_comment_list:
                comment += (each_comment.split('|')[2].lower())
        tags_analysis = self.tags_analysis(comment)
        pic_path = 'C:/Users/Administrator/Desktop/22-13041Q55010.jpg'
        self.drawWordCloud(tags_analysis, pic_path, 'miku')

class DrawPic:
    def deal_list_data(self, data):
        temp = data[:30]
        names_data, music_data = [], []
        for i in temp:
            if len(i[0]) > 5:
                name = i[0][:int(len(i[0])/2)] + '\n' + i[0][int(len(i[0])/2):]
                names_data.append(name)
            else:
                names_data.append(i[0])
            music_data.append(i[1])
        plt.figure(figsize=(30, 8))
        plt.plot(range(0,30), music_data, linewidth=1, color='red')
        plt.xticks(range(0, 30), names_data)
        plt.title('评论超过1000的歌手排名')
        plt.ylabel('评论超过1000歌曲数量')
        plt.xlabel('名字')
        data_xy = zip(range(0, 30), music_data)
        for x, y in data_xy:
            plt.text(x, y + 0.1, y, color='blue', fontsize=10)
        plt.show()


if __name__ == '__main__':
    mon = Mongo()
    aly = Analysis()
    dp = DrawPic()
    # aly.comment_analysis('159692') # 根据id画词云
    # dp.deal_list_data(aly.made_figure(1000)) # 绘制评论>1000的歌手排名
    artists = mon.collection_artist.find({'store_type':'Not Start', 'type':'华语女歌手'})
    for i in artists:
        if mon.collection.find({'singer_id':i['id']}).count() > 0:
            print(i['name'])
