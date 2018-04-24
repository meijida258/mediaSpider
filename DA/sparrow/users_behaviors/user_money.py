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
    def __init__(self, start_date:list, end_date:list):
        self.start_date = start_date
        self.end_date = end_date

    # 获取时间段内的记录
    @time_clock
    def get_pay_log(self)-> pandas.DataFrame():
        # 查询时间段内的数据，只返回用户id，价格，时间
        apple_pay_log = mongo.apple_pay_log.find({'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                                          '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
                                                 {'_id':0, 'source':1, 'price':1, 'date':1})
        apple_pay_df = pandas.DataFrame(list(apple_pay_log))

        android_pay_log = mongo.android_pay_log.find({'paid':True,'pay_date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                                          '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
                                                 {'_id':0, 'source':1, 'price':1, 'pay_date':1})
        android_pay_df = pandas.DataFrame(list(android_pay_log))
        android_pay_df.rename(columns={'pay_date':'date'}, inplace=True) # 修改列名

        users_pay_df = pandas.concat([apple_pay_df, android_pay_df]) # 合并数据

        users_pay_df['date'] = users_pay_df['date'].apply(lambda x:str(x).split(' ')[0]) # 日期格式修改为%y-%m-%d
        users_pay_df.rename(columns={'source':'user_id'}, inplace=True)

        return users_pay_df

    @time_clock
    def get_user_pay_sum(self, data):
        # 根据user_id返回求和的数据
        pay_sum = data['price'].groupby(data['user_id']).sum()
        pay_sum_df = pay_sum.to_frame()
        pay_sum_df['user_id'] = pay_sum_df.index
        pay_sum_df.rename(columns={'price':'pay_price'}, inplace=True)
        return pay_sum_df

    @time_clock
    def get_play_log(self):
        play_log = mongo.ext_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}}},
                {'$group':{'_id':'$user_id', 'play_count':{'$sum':1}, 'play_amount':{'$sum':'$consume'}}}
            ]
        )
        play_df = pandas.DataFrame(list(play_log)) # 转为Dataframe格式
        play_df.rename(columns={'_id':'user_id'}, inplace=True) # 修改列名

        return play_df

    @time_clock
    def get_gift_log(self):
        gift_log = mongo.gift_log.find({'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
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
    um = UserMoney(start_date=[2018, 4, 1, 0,0], end_date=[2018,4,10,0,0])
    # 充值
    pay_df = um.get_pay_log()
    pay_sum_df = um.get_user_pay_sum(data=pay_df)
    # 游戏
    play_df = um.get_play_log()
    # 礼物
    gift_df = um.get_gift_log()
    gift_sum_df = um.get_user_gift_sum(gift_df)
    # 合并数据
    pay_and_play_log = pandas.merge(play_df, pay_sum_df, how='outer',on=['user_id'])
    all_users_result = pandas.merge(pay_and_play_log, gift_sum_df, how='outer',on=['user_id']).fillna(0)
    # 剔除非人
    normal_users = um.get_normal_users()
    result = pandas.merge(normal_users, all_users_result, how='inner', on=['user_id'])

    result.to_csv('user_pp.csv')
    mongo.client.close()