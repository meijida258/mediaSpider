# 分析每个用户的行为
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy
import os, csv, re
import matplotlib.pyplot as plt
from sparrow.sparrow_query import Analysis as AnalysisMain
from sparrow.daily_analysis import AnalysisTools
from sparrow.longtime_analysis import Analysis as AnalysisLongTime

source_data_path = 'D:/sparrow_data/'
file_save_path = 'D:/sparrow_data/main_analysis/'

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.sparrow_main
        self.all_users = self.db.users
        self.users_login_log = self.db.login_log
        self.beginner_card_log = self.db.beginner_card_log
        self.db2 = self.client.sparrow_analysis
        self.daily_data = self.db2.daily_deal_data

class BehaviorsAnalysis:

    # 用户付费行为分析
    def user_pay_data(self):
        csv_head = ['user_id', 'user_regist_date', '当日付费', '3天付费', '7天付费', '14天付费', '30天付费', '30天以上']

        users = mongo.all_users.find({'username': {'$regex': r'^(?!robot_[0-9]{5})'}})
        data = []
        for user in users:
            save_data = {}
            save_data['user_id'] = str(user['_id'])
            save_data['user_regist_date'] = user['regist_date']
            # 注册后一定日期内付费
            query_list = [[0, 1], [1, 3], [3, 7], [7, 14], [14, 30], [30, 100]]
            for query_days in query_list:
                st_date_timestamp = analysis_longtime.get_timestamp(save_data['user_regist_date'].year,
                                                                    save_data['user_regist_date'].month,
                                                                    save_data['user_regist_date'].day,
                                                                    save_data['user_regist_date'].hour)
                st_date = analysis_longtime.get_datetime(st_date_timestamp, -query_days[0])
                end_date = analysis_longtime.get_datetime(st_date_timestamp, -query_days[1])
                pay_data = analysis_main.get_user_pay_log({'user_id': save_data['user_id']}, st_date=st_date, end_date=end_date)
                save_data[csv_head[query_list.index(query_days)+2]] = [[pay_data['third_pay_count'] + pay_data['coin_trader_count'] + pay_data['apple_pay_count']],
                                             [pay_data['third_pay_amount'] + pay_data['coin_trader_amount']+pay_data['apple_pay_amount']]]
            data.append(save_data)
        #写入文件
        file_path = file_save_path + 'pay_analysis.csv'
        analysis_longtime.write_csv(file_path, head=csv_head, keys=csv_head, data=data)

    def user_pay_analysis(self):
        csv_head = ['user_id', 'user_regist_date', '当日付费', '3天付费', '7天付费', '14天付费', '30天付费', '30天以上']
        data = pandas.read_csv(file_save_path + 'pay_analysis.csv')
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        pay_user_count, pay_amount = [0]*6, [0]*6
        for row in range(0, data.shape[0]):
            for head in csv_head[2:]:
                if int(re.findall(r'\[\[(.*)\], \[(.*)\]\]', data.ix[row, head])[0][0]) > 0:
                    pay_user_count[csv_head.index(head)-2] += 1
                    pay_amount[csv_head.index(head)-2] += round(float(re.findall(r'\[\[(.*)\], \[(.*)\]\]', data.ix[row, head])[0][1]))
        pay_proportion = numpy.array(pay_user_count) / data.shape[0]
        pay_average = numpy.array(pay_amount) / numpy.array(pay_user_count) / 100

        ax1.bar(numpy.arange(len(pay_proportion)), pay_proportion, tick_label=csv_head[2:], width=0.2, color='blueviolet')
        ax1.set_ylabel('付费率')
        ax11 = ax1.twinx()
        ax11.plot(numpy.arange(len(pay_proportion)), pay_average, color='plum')
        ax11.set_ylabel('平均付费金额')
        for i in range(0, len(pay_proportion)):
            ax11.text(i, pay_average[i], int(pay_average[i]))
            ax1.text(i-0.05 ,pay_proportion[i]+0.001, '%.2f%%' %(pay_proportion[i]*100))
            print(i)
        plt.savefig(file_save_path+'user_behavior_pay.jpg')
        plt.show()

    def get_datetime_list(self, iso_datetime):
        return [iso_datetime.year, iso_datetime.month, iso_datetime.day, iso_datetime.hour]

if __name__ == '__main__':
    mongo = Mongo()
    behaviors_analysis = BehaviorsAnalysis()
    analysis_main = AnalysisMain()
    analysis_longtime = AnalysisLongTime()
    start_time = time.time()
    # behaviors_analysis.user_pay_data()
    behaviors_analysis.user_pay_analysis()
    print(time.time()-start_time)