#-------------------------------------------------------------------------
#   程序：users_behavior
#   日期：2018.4.12
#   功能：获取抽奖的数据
#-------------------------------------------------------------------------
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy


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


class UserLotteryLog:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_users_lottery_data(self):
        users_lottery_data = mongo.lottery_log.find(
            {'date': {'$gte': datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                      '$lte': datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
            {'date': 1, 'source': 1, '_id': 0})
        return list(users_lottery_data)

    def lottery_analysis(self, users_lottery_data):
        users_lottery_df = pandas.DataFrame(users_lottery_data)
        users_lottery_df.rename(columns={'source': 'user_id', 'date': 'lottery_date'}, inplace=True)
        users_lottery_df['lottery_date_day'] = users_lottery_df['lottery_date'].apply(lambda x: str(x).split(' ')[0])
        lottery_data = users_lottery_df['lottery_date'].groupby(
            [users_lottery_df['user_id'], users_lottery_df['lottery_date_day']]).count()
        lottery_data.to_csv('lottery_data.csv')

    def get_lottery_award(self):
        lottery_log = mongo.lottery_log.aggregate(
            [
                {'$match': {'date': {
                    '$gte': datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                    '$lte': datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}}},
                {'$group': {'_id': '', 'lottery_times': {'$sum': 1}, 'lottery_award':{'$sum':'$lottery_award.reward'}, 'user_id':{'$push':'$source'}}}
            ]
        )
        return list(lottery_log)

if __name__ == '__main__':
    mongo = Mongo()
    start_date, end_date = [2018,3,17], [2018,4,10]
    ull = UserLotteryLog(start_date=start_date, end_date=end_date)
    users_lottery_data = ull.get_users_lottery_data()
    ull.lottery_analysis(users_lottery_data)

    lottery_award_data = ull.get_lottery_award()
    print(len(set(lottery_award_data[0]['user_id'])))
    print(lottery_award_data[0]['lottery_award'])
    print(lottery_award_data[0]['lottery_award'] / lottery_award_data[0]['lottery_times'])