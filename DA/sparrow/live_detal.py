#-------------------------------------------------------------------------
#   程序：users_remain
#   日期：2018.4.12
#   功能：获取一段时间主播的魅力收入和房间流水
#-------------------------------------------------------------------------

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import pandas, numpy
from pymongo import MongoClient
import datetime, time

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
        self.guard_log = self.db.guard_log
        self.room_log = self.db.room_log
        # 过滤后的数据集
        self.db2 = self.client.sparrow_analysis
        self.game_daily_log = self.db2.game_daily_log
        self.users_daily_log = self.db2.users_daily_log
        self.reamin_data = self.db2.users_remain
class GetDetail:
    def __init__(self, start_date:list, end_date:list):
        self.start_date = start_date
        self.end_date = end_date

    # 获取用户的基本信息，昵称，总魅力
    def get_users_detail(self):
        users = mongo.users.find({'username': {'$regex': r'^(?!robot_[0-9]{5})'}},
                                 {'_id': 1, 'user_info.nickname':1})
        users_df = pandas.DataFrame(list(users))
        users_df.rename(columns={'_id': 'user_id', 'user_info':'nickname'}, inplace=True)
        users_df['user_id'] = users_df['user_id'].apply(lambda x: str(x))
        users_df['nickname'] = users_df['nickname'].apply(lambda x:x['nickname'])
        # users_df['gift_purchase_total'] = users_df['gift_purchase_total'].apply(lambda x:x['gift_purchase'])
        return users_df

    # 获取时间段收礼记录
    def get_gift_detail(self):
        gitf_log = mongo.gift_log.find({'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
                                       {'_id':0, 'date':1, 'target':1, 'gift.price':1})
        gift_df = pandas.DataFrame(list(gitf_log))
        gift_df.rename(columns={'target': 'user_id', 'gift':'gift_price'}, inplace=True)  # 修改列名
        gift_df['gift_price'] = gift_df['gift_price'].apply(lambda x:x['price'])

        # 根据获取的基础数据，根据id求和
        gift_sum_df = self.get_gift_sum_by_id(gift_df)
        return gift_sum_df

    # 通过礼物数据，根据id求和
    def get_gift_sum_by_id(self, data):
        gift_sum = data['gift_price'].groupby(data['user_id']).sum() # 根据user_id求gift_price的和
        gift_sum_df = gift_sum.to_frame() # series格式转dataframe
        gift_sum_df['user_id'] = gift_sum_df.index
        return gift_sum_df

    # 获取时间段内守护记录,并求和
    def get_guard_detail(self):
        guard_log = mongo.guard_log.find({'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}},
                                         {'target':1, '_id':0, 'guard.price':1})
        guard_df = pandas.DataFrame(list(guard_log))
        guard_df.rename(columns={'target':'user_id', 'guard':'guard_price'}, inplace=True)
        guard_df['guard_price'] = guard_df['guard_price'].apply(lambda x:x['price'])

        guard_sum_df = self.get_guard_sum_by_id(guard_df)
        return guard_sum_df

    def get_guard_sum_by_id(self, data):
        guard_sum = data['guard_price'].groupby(data['user_id']).sum() # 根据user_id求guard_price的和
        guard_sum_df = guard_sum.to_frame()
        guard_sum_df['user_id'] = guard_sum_df.index # 将index作为id添加进frame
        return guard_sum_df

    # @check_time
    def get_ext_detail(self):
        ext_log = mongo.ext_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)},
                           'desc':'cost'}},
                {'$group':{'_id':'$room_id', 'game_amount':{'$sum':'$consume'}}}
            ]
        )
        ext_df = pandas.DataFrame(list(ext_log))

        ext_df.rename(columns={'_id':'user_id'}, inplace=True)
        return ext_df

    # def check_time(self, func):
    #     start_time = time.clock()
    #     func()
    #     return time.clock() - start_time

    def get_room_log(self):
        room_log = mongo.room_log.aggregate(
            [
                {'$match':{'close_date':{'$gte':datetime.datetime(self.start_date[0], self.start_date[1], self.start_date[2], 0, 0),
                                   '$lte':datetime.datetime(self.end_date[0], self.end_date[1], self.end_date[2], 0, 0)}}},
                {'$group':{'_id':'$anchor', 'charm_amount':{'$sum':'$charm_income'}}}
            ]
        )
        room_df = pandas.DataFrame(list(room_log))
        room_df.rename(columns={'_id':'user_id'}, inplace=True)
        return room_df
if __name__ == '__main__':
    mongo = Mongo()
    start_date, end_date = [2018, 4, 1, 0,0], [2018,4,10,0,0]
    gd = GetDetail(start_date=start_date, end_date=end_date)
    users_df = gd.get_users_detail()
    # gift_df = gd.get_gift_detail()
    # guard_df = gd.get_guard_detail()
    ext_df = gd.get_ext_detail()
    room_df = gd.get_room_log()
    # users_gift_df = pandas.merge(users_df, gift_df, on=['user_id'])    # 根据用户id， 将用户信息与礼物frmae合并， 内连接
    # users_gift_guard_df = pandas.merge(users_gift_df, guard_df, how='outer', on=['user_id']).fillna(0)    # 根据用户id， 将上表与守护表合并, 外链接
    # users_gift_guard_df['charm_amount'] = users_gift_guard_df['gift_price'] + users_gift_guard_df['guard_price']
    # users_result_df = pandas.merge(users_gift_guard_df, ext_df, on=['user_id']) # 根据用户id， 将上表与游戏合并， 内连接
    # users_result_df.to_csv('users_gift_guard_df.csv', header=['用户id', '昵称', '礼物收入', '守护收入', '魅力总收入', '房间游戏总计'], index=False)

    u2 = pandas.merge(users_df, room_df, on=['user_id'])
    u2_ = pandas.merge(u2, ext_df, on=['user_id'])
    file_name = 'anchor_log{}-{}'.format('_'.join(str(i) for i in start_date[:3]), '_'.join(str(i) for i in end_date[:3]))
    u2_.to_csv('{}.csv'.format(file_name), header=['用户id', '昵称', '魅力总收入', '游戏下注总计'], index=False)
    mongo.client.close()