# -*- coding: UTF-8 -*-
import jieba.analyse, wordcloud, xlwt
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from pymongo import MongoClient
from wordcloud import WordCloud, STOPWORDS

class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.video_db = self.client.Bilibili
        self.video_collection = self.video_db.Video

class Analysis():
    def __init__(self):
        niconico = True
        jieba.load_userdict('C:/test_py/spiderTest/media_spider/bilibili/dict.txt')

    def get_all_tags(self):
        if TYPENAME:
            video_dicts = mon.video_collection.find({'typename':TYPENAME})
        else:
            video_dicts = mon.video_collection.find()
        result_tags = ''
        for video_dict in video_dicts:
            result_tags += video_dict['title']
        result_tags = result_tags[:-1].upper()
        return result_tags[:-1]

    def tags_analysis(self, result_tags):
        result = jieba.analyse.extract_tags(result_tags, topK=102, withWeight=True, allowPOS=())
        return result

    def drawWordCloud(self, result):
        wordcloud = WordCloud(background_color='white', max_font_size=100, relative_scaling=.2, stopwords=STOPWORDS.add('投稿')).fit_words(result)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()

    def get_word_cloud(self):
        # 获取所有的标签
        result_tags = self.get_all_tags()
        # 获取处理后的标签
        result = self.tags_analysis(result_tags)
        # 绘制词云
        self.drawWordCloud(result)

    def get_famous_video(self):
        if TYPENAME:
            video_dicts = mon.video_collection.find({'typename':TYPENAME})
        else:
            video_dicts = mon.video_collection.find()
        famous_video_result = []
        for video_dict in video_dicts:
            if video_dict['play'] > 500000 and video_dict['video_review'] > 2000:
                temp_dict = {}
                temp_dict['play'] = video_dict['play']
                temp_dict['title'] = video_dict['title']
                temp_dict['link'] = video_dict['video_link']
                temp_dict['review'] = video_dict['video_review']
                famous_video_result.append(temp_dict)
        return famous_video_result

    def write_famous_video_result(self):
        famous_video_result = self.get_famous_video()
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet('zw', cell_overwrite_ok=True)
        row = 0
        for each_dict in famous_video_result:
            sheet.write(row,0,each_dict['title'])
            sheet.write(row, 1, each_dict['play'])
            sheet.write(row, 2, each_dict['review'])
            sheet.write(row, 3, each_dict['link'])
            row += 1
        if TYPENAME:
            book.save(('%s_famous_video.xls' % TYPENAME).decode('utf-8').encode('gbk'))
        else:
            book.save('famous_video.xls')

    def get_each_month_create(self, video_dicts):
        create_date_result = {}
        for video_dict in video_dicts:
            create_date = video_dict['create'].split(' ')[0]
            if  create_date.split('-')[1] == '08':
                if create_date_result.has_key(create_date):
                    create_date_result[create_date] += 1
                else:
                    create_date_result[create_date] = 1
        per_day_play = range(1, 32)
        for key in create_date_result:
            day = int(str(key).split('-')[-1])
            per_day_play[day - 1] = create_date_result[key]
        return per_day_play


    def draw_line_plots(self):
        x = range(1, 32)
        y_values = {}
        type_names = [u'MMD·3D', u'宅舞', u'鬼畜调教']
        for type_name in type_names:
            y_values['y%s' % str(type_names.index(type_name) + 1)] = self.get_each_month_create(mon.video_collection.find({'typename':type_name}))
        # 设置折线粗细，颜色
        line1 = pl.plot(x, y_values['y1'],linewidth=0.6, color='red', marker='o', label=type_names[0])
        for xy in zip(x, y_values['y1']):
            pl.annotate(xy[1], xy=xy, xytext=(-10, 10), textcoords='offset points', color='red')
        line2 = pl.plot(x, y_values['y2'], linewidth=0.6, color='green', marker='o', label=type_names[1])
        for xy in zip(x, y_values['y2']):
            pl.annotate(xy[1], xy=xy, xytext=(-10, 10), textcoords='offset points', color='green')
        line3 = pl.plot(x, y_values['y3'], linewidth=0.6, color='blue', marker='o', label=type_names[2])
        for xy in zip(x, y_values['y3']):
            pl.annotate(xy[1], xy=xy, xytext=(-10, 10), textcoords='offset points', color='blue')
        pl.legend(loc='upper right')
        # 设置左边刻度
        ax = pl.gca()
        ax.set_xticks(np.linspace(-1, 32, 34))
        ax.set_xlabel(u'8月')
        ax.set_ylabel(u'投稿数量')
        pl.xlim(0, 32) # x轴范围
        pl.show()
if __name__ == '__main__':
    TYPENAME = None
    mon = Mongo()
    analy = Analysis()
    # analy.get_word_cloud() # 生成TYPENAME的词云
    # analy.write_famous_video_result() # 生成TYPENAME的高播放excel表
    analy.draw_line_plots()