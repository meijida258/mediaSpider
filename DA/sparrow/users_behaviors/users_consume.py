#-------------------------------------------------------------------------
#   程序：users_remain
#   日期：2018.4.12
#   功能：获取
#-------------------------------------------------------------------------

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import pandas, numpy
from pymongo import MongoClient
import datetime, time
from users_behaviors.users_pay import UserPayAnalysis

def time_clock(func):
    def wrapper(*args, **kwargs):
        start_time = time.clock()
        r = func(*args, **kwargs)
        print('{}()耗时{}'.format(func.__name__, time.clock()-start_time))
        return r
    return wrapper

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        # 主数据集
        self.db = self.client.sparrow_main
        self.users = self.db.users
        self.ext_log = self.db.extension_log
        self.apple_pay_log = self.db.apple_iap_log
        self.android_pay_log = self.db.recharge_orders
        self.gift_log = self.db.gift_log
        # 过滤后的数据集
        self.db2 = self.client.sparrow_analysis
        self.game_daily_log = self.db2.game_daily_log
        self.users_daily_log = self.db2.users_daily_log
        self.reamin_data = self.db2.users_remain

class UserMoney:
    def __init__(self):
        # self.start_date = start_date
        # self.end_date = end_date
        pass

    @time_clock
    def get_play_log(self, start_date, end_date):
        play_log = mongo.ext_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                   '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}}},
                {'$group':{'_id':'$user_id', 'play_count':{'$sum':1}, 'play_amount':{'$sum':'$consume'}}}
            ]
        )
        play_df = pandas.DataFrame(list(play_log)) # 转为Dataframe格式
        play_df.rename(columns={'_id':'user_id'}, inplace=True) # 修改列名

        return play_df

    @time_clock
    def get_gift_log(self, start_date, end_date):
        gift_log = mongo.gift_log.find({'date':{'$gte':datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                   '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}},
                                       {'_id':0, 'date':1, 'source':1, 'gift.price':1})
        gift_df = pandas.DataFrame(list(gift_log))
        gift_df.rename(columns={'source': 'user_id', 'gift':'gift_price'}, inplace=True)  # 修改列名
        gift_df['gift_price'] = gift_df['gift_price'].apply(lambda x:x['price'])
        return gift_df

    @time_clock
    def get_user_gift_sum(self, data):
        gift_sum = data['gift_price'].groupby(data['user_id']).sum() # 根据user_id求gift_price的和
        gift_sum_df = gift_sum.to_frame() # series格式转dataframe
        gift_sum_df['user_id'] = gift_sum_df.index
        return gift_sum_df

    @time_clock
    def get_normal_users(self):
        users = mongo.users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}}, {'_id':1})
        users_df = pandas.DataFrame(list(users))
        users_df.rename(columns={'_id':'user_id'}, inplace=True)
        users_df['user_id'] = users_df['user_id'].apply(lambda x:str(x))
        return users_df

if __name__ == '__main__':
    mongo = Mongo()
    up = UserPayAnalysis()
    start_date, end_date = [2018, 4, 18, 0, 0], [2018, 4, 19, 0, 0]
    um = UserMoney()
    # 充值
    pay_df_apple = up.get_pay_log_apple(start_date, end_date)
    pay_df_android = up.get_pay_log_android(start_date, end_date)
    pay_df_android.rename(columns={'pay_date': 'date'}, inplace=True)
    users_pay_df = pandas.concat([pay_df_apple, pay_df_android])  # 合并数据
    users_pay_df['date'] = users_pay_df['date'].apply(lambda x: str(x).split(' ')[0])  # 日期格式修改为%y-%m-%d
    users_pay_df.rename(columns={'source': 'user_id'}, inplace=True)
    pay_sum_df = up.get_user_pay_sum(data=users_pay_df)

    # 游戏
    play_df = um.get_play_log(start_date, end_date)
    # 礼物
    gift_df = um.get_gift_log(start_date, end_date)
    print(gift_df)
    exit()
    gift_sum_df = um.get_user_gift_sum(gift_df)
    # 合并数据
    pay_and_play_log = pandas.merge(play_df, pay_sum_df, how='outer',on=['user_id'])
    all_users_result = pandas.merge(pay_and_play_log, gift_sum_df, how='outer',on=['user_id']).fillna(0)
    # 剔除非人
    normal_users = um.get_normal_users()
    result = pandas.merge(normal_users, all_users_result, how='inner', on=['user_id'])

    result.to_csv('user_pp.csv', index=False)
    mongo.client.close()
else:
    mongo = Mongo()
    um = UserMoney()