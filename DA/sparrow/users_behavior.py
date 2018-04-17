#-------------------------------------------------------------------------
#   程序：users_behavior
#   日期：2018.4.12
#   功能：获取特定行为的数据
#-------------------------------------------------------------------------
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
from sparrow.tools import get_datetime, get_timestamp, write_csv

source_data_path = 'D:/sparrow_data/'
file_save_path = 'D:/sparrow_data/main_analysis/'

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.sparrow_main
        self.all_users = self.db.users
        self.users_login_log = self.db.login_log
        self.apple_pay = self.db.apple_iap_log
        self.daily_data = self.db.daily_deal_data
        self.third_pay = self.db.recharge_orders
        self.daily_task_log = self.db.daily_task_log
        self.lottery_log = self.db.lottery_log
        self.db2 = self.client.sparrow_analysis

class UserPayAnalysis:
    def __init__(self, off_day, pic_name, csv_name):
        self.pic_name = pic_name
        self.csv_name = csv_name
        self.off_day = off_day
        self.time_today = time.time()
        self.st_year, self.st_month, self.st_day = int(
            time.strftime('%Y', time.localtime(self.time_today - 86400 * (self.off_day + 2)))), int(
            time.strftime('%m', time.localtime(self.time_today - 86400 * (self.off_day + 2)))), int(
            time.strftime('%d', time.localtime(self.time_today - 86400 * (self.off_day + 2))))
        self.end_year, self.end_month, self.end_day = int(
            time.strftime('%Y', time.localtime(self.time_today - 86400 * (self.off_day + 1)))), int(
            time.strftime('%m', time.localtime(self.time_today - 86400 * (self.off_day + 1)))), int(
            time.strftime('%d', time.localtime(self.time_today - 86400 * (self.off_day + 1))))
    # 用户付费行为分析
    def user_pay_data(self):
        csv_head = ['user_id', 'user_regist_date', '当日付费', '3天付费', '7天付费', '14天付费']
        # users = mongo.all_users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}})
        users = mongo.all_users.find({'regist_date':{"$gte":datetime.datetime(self.st_year, self.st_month, self.st_day, 0, 0)}})
        data = []
        for user in users:
            save_data = {}
            save_data['user_id'] = str(user['_id'])
            save_data['user_regist_date'] = user['regist_date']
            # 注册后一定日期内付费
            query_list = [[0, 1], [1, 3], [3, 7], [7, 14]]
            for query_days in query_list:
                st_date_timestamp = get_timestamp(save_data['user_regist_date'].year,
                                                                    save_data['user_regist_date'].month,
                                                                    save_data['user_regist_date'].day,
                                                                    save_data['user_regist_date'].hour)
                st_date = get_datetime(st_date_timestamp, -query_days[0])
                end_date = get_datetime(st_date_timestamp, -query_days[1])
                pay_data = self.get_user_pay_log({'user_id': save_data['user_id']}, st_date=st_date, end_date=end_date)
                save_data[csv_head[query_list.index(query_days)+2]] = [[pay_data['third_pay_count']  + pay_data['apple_pay_count']],
                                             [pay_data['third_pay_amount'] + pay_data['apple_pay_amount']]]
            data.append(save_data)
        #写入文件
        file_path = file_save_path + '{}.csv'.format(self.csv_name)
        write_csv(file_path, head=csv_head, keys=csv_head, data=data)

    # 获取某个id的支付
    def get_user_pay_log(self, user_id:dict, st_date, end_date):
        print(user_id)
        pay_data = {}
        third_pay_log = mongo.third_pay.aggregate(
            [
                {'$match':{'pay_date':{"$gte":datetime.datetime(st_date[0],st_date[1],st_date[2],0,0),
                                       '$lte':datetime.datetime(end_date[0],end_date[1],end_date[2],0,0)},
                           'paid':True, 'source':user_id['user_id']}},
                {'$group':{'_id':'', 'pay_count':{'$sum':1}, 'pay_amount':{'$sum':'$price'}}}
            ]
        )
        try:
            third_pay_log_list = list(third_pay_log)[0]
            pay_data['third_pay_count'] = third_pay_log_list['pay_count']
            pay_data['third_pay_amount'] = third_pay_log_list['pay_amount']
        except:
            pay_data['third_pay_count'], pay_data['third_pay_amount'] = 0, 0


        apple_pay_log = mongo.apple_pay.aggregate(
            [
                {'$match': {'date': {"$gte": datetime.datetime(st_date[0], st_date[1], st_date[2], 0, 0),
                                         '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)},
                            'source':user_id['user_id']}},
                {'$group': {'_id': '', 'pay_count': {'$sum': 1}, 'pay_amount': {'$sum': '$price'}}}
            ]
        )
        try:
            apple_pay_log_list = list(apple_pay_log)[0]
            pay_data['apple_pay_count'] = apple_pay_log_list['pay_count']
            pay_data['apple_pay_amount'] = apple_pay_log_list['pay_amount']
        except:
            pay_data['apple_pay_count'], pay_data['apple_pay_amount'] = 0, 0
        print(pay_data)
        return pay_data

    def user_pay_analysis(self):
        csv_head = ['user_id', 'user_regist_date', '当日付费', '3天付费', '7天付费', '14天付费']
        data = pandas.read_csv(file_save_path + '{}.csv'.format(self.csv_name))
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        pay_user_count, pay_amount = [0]*4, [0]*4
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
            try:
                ax11.text(i, pay_average[i], int(pay_average[i]))
            except:
                ax11.text(i, pay_average[i], 0)
            ax1.text(i-0.05 ,pay_proportion[i]+0.001, '%.2f%%' %(pay_proportion[i]*100))
        pic_path = file_save_path+'{}.jpg'.format(self.pic_name)

        plt.savefig(pic_path)
        plt.show()

    def get_datetime_list(self, iso_datetime):
        return [iso_datetime.year, iso_datetime.month, iso_datetime.day, iso_datetime.hour]

class UserLotteryLog:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_lottery_log(self):
        lottery_log = mongo.lottery_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(self.start_date[0],self.start_date[1],self.start_date[2],0,0),
                                   '$lte':datetime.datetime(self.end_date[0],self.end_date[1],self.end_date[2],0,0)}}},
                {'$group':{'_id':'$source', 'lottery_date':{'$push':'$date'}}}
            ]
        )
        return list(lottery_log)

    # def lottery_analysis(self, lottery_log):
    #     for lottery_data in lottery_log:

if __name__ == '__main__':
    mongo = Mongo()
    behaviors_analysis = UserPayAnalysis(off_day=15, pic_name='30', csv_name='30天支付')
    # behaviors_analysis.user_pay_data()
    # behaviors_analysis.user_pay_analysis()
    # -----------
    start_date, end_date = [2018,4,7], [2018,4,8]
    ull = UserLotteryLog(start_date=start_date, end_date=end_date)
    print(ull.get_lottery_log())