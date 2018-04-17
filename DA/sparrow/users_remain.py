#-------------------------------------------------------------------------
#   程序：users_remain
#   日期：2018.4.12
#   功能：获取留存数据
#-------------------------------------------------------------------------

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from sparrow.daily_analysis import at
from sparrow.tools import get_datetime
from pymongo import MongoClient
import time, datetime
import bson, pandas, numpy

class UsersRemain:
    # 查询某天的新注册用户，以channel分组，返回user_id
    def get_new_users(self, off_day):
        start_date = get_datetime(time.time(), off_day+1)
        end_date = get_datetime(time.time(), off_day)
        print('查询{}新用户'.format(start_date))
        new_users_id = mon.users.aggregate(
            [
                {'$match': {
                    'regist_date': {"$gte": datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                    "$lte": datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}}},
                {'$group': {'_id': '$channel', 'user_id':{'$push':'$_id'}}}
            ]
        )
        return list(new_users_id)

    # 查询某天新注册用户，再查询某段时间的留存情况
    def remain_user_query(self, off_day, remain_query_list):
        new_users_id = self.get_new_users(off_day)
        source_dict = {}
        for source_data in new_users_id:
            source_dict[source_data['_id']] = set(source_data['user_id'])
        result = [source_dict]
        for remain_day in remain_query_list:
            this_day_login_users = self.login_user_query(off_day-remain_day)
            # 根据channel分别查交集，再以channel为key，结果交集为value，添加到result中
            remain_users = {}
            for channel_data in new_users_id:
                channel = channel_data['_id']
                # 对于不存在的设为空集合
                try:
                    remain_users[channel] = set(this_day_login_users) & set(channel_data['user_id'])
                except:
                    remain_users[channel] = set()
            result.append(remain_users)
        return result

    # 查询某天登录的用户
    def login_user_query(self, off_day):
        start_date = get_datetime(time.time(), off_day+1)
        end_date = get_datetime(time.time(), off_day)
        print('查询{}新用户留存情况'.format(start_date))
        login_users = mon.users_login_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                    "$lte": datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}}},
                {'$group':{'_id':'', 'user_id':{'$push':'$source'}}}
            ]
        )
        try:
            result = list(login_users)[0]['user_id']
        except:
            result = None
        if result:
            for index in range(0, len(result)):
                result[index] = bson.ObjectId(result[index])
        return result

    # 将[{channel:users_id}]转换为两个简单数组，一个channel，一个users_id个数
    def deal_remain_result_to_chart(self, result):
        # 先获取channel的list，确定顺序
        channel_keys = result[0].keys()
        # 每个查询时间段，对该时间段的数据进行处理
        deal_result = []
        for each_query_data in result:
            deal_query_data = []
            for channel_key in channel_keys:
                deal_query_data.append(len(each_query_data[channel_key]))
            deal_result.append(deal_query_data)
        return channel_keys, deal_result

    def deal_remain_result_to_dataframe(self, data ,keys):
        return pandas.DataFrame(data=data, columns=keys)

    def any_days_deal(self, data):
        result = {}
        for every_day_data in data:
            for channel in every_day_data.keys():
                try:
                    result[channel] += numpy.array(every_day_data[channel])
                except:
                    result[channel] = numpy.array(every_day_data[channel])
        return result



    def write_result_to_csv(self, file_path, dataframe):
        dataframe.to_csv(file_path, index=False, sep=',')
        print('保存{}完成'.format(file_path.split('/')[-1]))

    def deal_remain_result_to_dict(self, keys, data):
        result = {}
        for index in range(0, len(keys)):
            result[keys[index]] = [data[0][index], data[1][index], data[2][index]]
        return result

    def main(self, off_day, remain_query_list, result_type):
        result = self.remain_user_query(off_day, remain_query_list)
        keys, data = self.deal_remain_result_to_chart(result)
        if result_type == 'data_frame':
            data_frame = self.deal_remain_result_to_dataframe(data=data, keys=keys)
            return data_frame
        elif result_type == 'source_data_type':
            return [keys, data]
        elif result_type == 'dict_type':
            return self.deal_remain_result_to_dict(list(keys), data)

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        # 过滤后的数据集
        self.db = self.client.sparrow_analysis
        self.game_daily_log = self.db.game_daily_log
        self.users_daily_log = self.db.users_daily_log
        self.reamin_data = self.db.users_remain
        # 主数据集
        self.db2 = self.client.sparrow_main
        self.users = self.db2.users
        self.ext_log = self.db2.extension_log
        self.users_login_log = self.db2.login_log
if __name__ == '__main__':
    ur = UsersRemain()
    mon = Mongo()
    # 查询的时间，向前推off_day天，remain_query_list隔天
    # off_day = 15
    # remain_query_list = [1,3,7]
    # data_frame = ur.main(off_day=off_day, remain_query_list=remain_query_list)

    # 查询多天
    start_day, end_day = 10, 12
    remain_query_list = [1, 3, 7]
    result = []
    for off_day in range(start_day, end_day):
        source_data = ur.main(off_day=off_day, remain_query_list=remain_query_list, result_type='dict_type')
        result.append(source_data)
    deal_result_dict = ur.any_days_deal(result)
    deal_result_dict_value_array = numpy.array(list(deal_result_dict.values()))
    deal_result_data_frame = ur.deal_remain_result_to_dataframe(data=deal_result_dict_value_array.T, keys=deal_result_dict.keys())
    ur.write_result_to_csv('user_reamin.csv', deal_result_data_frame)
else:
    ur = UsersRemain()
    mon = Mongo()