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
import pymongo
import time, datetime
import pandas, numpy
import tqdm
import itertools

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
        self.db2 = self.client.sparrow_analysis

        self.gift_log = self.db.gift_log
        self.gift_lottery_log = self.db.gift_lottery_log

class GiftLotteryLog:
    def __init__(self):
        # self.start_date = start_date
        # self.end_date = end_date
        pass

    def get_gift_lottery_award(self, start_date, end_date):
        gift_lottery_award = mongo.gift_lottery_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)}},
            {'date': 1, 'source': 1, '_id': 0, 'reward':1})
        return gift_lottery_award

    def lottery_analysis(self, gift_lottery_award, gift_lottery_log):
        gift_lottery_award_df = pandas.DataFrame(list(gift_lottery_award))
        gift_lottery_award_df['date'] = gift_lottery_award_df['date'].apply(self.time_offset)
        try:
            os.remove('lucky_gift/lucky_gift_award_log.csv')
        except:pass
        finally:
            gift_lottery_award_df.to_csv('lucky_gift/lucky_gift_award_log.csv')
        count = gift_lottery_log.count()

        gift_lottery_log_gen = (i for i in gift_lottery_log)
        try:
            os.remove('lucky_gift/lucky_gift_send_log.csv')
        except:pass
        for i in tqdm.tqdm(range(int(count / 10000)+1)):
            gift_lottery_log_df = pandas.DataFrame(list(itertools.islice(gift_lottery_log_gen, 0, 10000)))
            try:
                gift_lottery_log_df['gift_price'] = gift_lottery_log_df['gift'].apply(lambda x:int(x['price']))
            except:print(gift_lottery_log_df)
            gift_lottery_log_df['gift'] = gift_lottery_log_df['gift'].apply(lambda x: x['name'])
            gift_lottery_log_df['date'] = gift_lottery_log_df['date'].apply(self.time_offset)
            if os.path.exists('lucky_gift/lucky_gift_send_log.csv'):
                gift_lottery_log_df.to_csv('lucky_gift/lucky_gift_send_log.csv', mode='a')
            else:
                gift_lottery_log_df.to_csv('lucky_gift/lucky_gift_send_log.csv', mode='w')

    def get_gift_lottery_log(self, start_date, end_date):
        gift_lottery_log = mongo.gift_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)},
             'gift.lottery':True},
            {'date': 1, 'source': 1, '_id': 0, 'gift.price': 1,'gift.name':1})
        return gift_lottery_log

    def get_users(self):
        all_users = mongo.all_users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}}, {'channel':1,'user_info.nickname':1})
        all_user = pandas.DataFrame(list(all_users))
        all_user.rename(columns={'user_info': 'name', '_id': 'source'}, inplace=True)
        all_user['name'] = all_user['name'].apply(lambda x: x['nickname'])
        all_user['source'] = all_user['source'].apply(lambda x: str(x))
        return all_user

    def time_offset(self, group):
        group = group + pandas.tseries.offsets.Hour(8)
        return datetime.datetime(group.year, group.month, group.day)

    def data_mining(self):
        all_user = self.get_users()

        gift_lottery_log_df = pandas.read_csv('lucky_gift/lucky_gift_send_log.csv')
        gift_lottery_log_df['gift_price'] = pandas.to_numeric(gift_lottery_log_df['gift_price'], errors='coerce')

        gift_lottery_log_groupby = gift_lottery_log_df.groupby(['date', 'source','gift'])['gift_price'].sum()
        gift_lottery_log_groupby = gift_lottery_log_groupby.reset_index()
        result_df = gift_lottery_log_groupby.merge(all_user, on=['source'])
        result_df.to_csv('lucky_gift/lucky_gift_log_gr.csv')

    def merge_data(self):
        send_log_df = pandas.read_csv('lucky_gift/lucky_gift_log_gr.csv')
        send_group_by_source = send_log_df.groupby(by=['date', 'source','name'])['gift_price'].sum()
        send_group_by_source = send_group_by_source.reset_index()
        send_group_by_source = send_group_by_source.merge(self.get_users(), on=['source'])

        reward_log_df = pandas.read_csv('lucky_gift/lucky_gift_award_log.csv')
        reward_group_by_date = reward_log_df.groupby(['date', 'source'])['reward'].sum()
        reward_group_by_date = reward_group_by_date.reset_index()
        merged_data = reward_group_by_date.merge(send_group_by_source, on=['date', 'source'])
        merged_data.to_csv('lucky_gift/merged_data.csv')

if __name__ == '__main__':
    mongo = Mongo()
    # mongo.gift_log.create_index([("gift.lottery", pymongo.ASCENDING)])
    # mongo.gift_log.remove({'date': {'$lte': datetime.datetime(2018, 8, 1, 0, 0)}})

    start_date, end_date = datetime.datetime(*[2018, 9, 1, 0, 0]), datetime.datetime(*[2018, 9, 3, 0, 0])
    st_time = time.clock()
    gl = GiftLotteryLog()
    gift_lottery_award = gl.get_gift_lottery_award(start_date, end_date)
    gift_lottery_log = gl.get_gift_lottery_log(start_date, end_date)
    gl.lottery_analysis(gift_lottery_award, gift_lottery_log)

    gl.data_mining()

    gl.merge_data()
    print(time.clock() - st_time)