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
import tqdm

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
        self.online_reward_log = self.db.online_reward_log
        self.daily_task_log = self.db.daily_task_log
        self.sign_in_log = self.db.sign_in_log
        self.gift_log = self.db.gift_log
        self.db2 = self.client.sparrow_analysis


class UserLotteryLog:
    def __init__(self):
        # self.start_date = start_date
        # self.end_date = end_date
        pass

    def get_users_lottery_data(self, start_date, end_date):
        users_lottery_data = mongo.lottery_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)}},
            {'date': 1, 'source': 1, '_id': 0, 'lottery_award.reward':1})
        return list(users_lottery_data)

    def get_users_online_reward_data(self, start_date, end_date):
        users_online_reward_data = mongo.online_reward_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)}},
            {'date': 1, 'source': 1, '_id': 0})

        daily_online_reward_data = pandas.DataFrame(list(users_online_reward_data))
        daily_online_reward_data['online_award'] = 10
        daily_online_reward_data.rename(columns={'source':'user_id'}, inplace=True)
        daily_online_reward_data['date'] = daily_online_reward_data['date'].apply(self.time_offset)
        online_reward_sum_data = daily_online_reward_data.groupby(['user_id', 'date'])['online_award'].sum()
        online_reward_sum_data = online_reward_sum_data.reset_index()

        return online_reward_sum_data

    def get_users_task_reward_data(self, start_date, end_date):
        users_task_reward_data = mongo.daily_task_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)},
             'lottery_tickets':0},
            {'date': 1, 'source': 1, '_id': 0, 'reward':1})
        daily_task_data = pandas.DataFrame(list(users_task_reward_data))
        daily_task_data.rename(columns={'source':'user_id', 'reward':'task_award'}, inplace=True)


        daily_task_data['date'] = daily_task_data['date'].apply(self.time_offset)

        task_sum_data = daily_task_data.groupby(['user_id', 'date'])['task_award'].sum()
        task_sum_data = task_sum_data.reset_index()
        return task_sum_data

    def get_users_sign_in_data(self, start_date, end_date):
        users_sign_in_data = mongo.sign_in_log.find(
            {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)},
             'lottery_tickets':0},
            {'date': 1, 'source': 1, '_id': 0, 'reward':1})

        daily_sign_in_data = pandas.DataFrame(list(users_sign_in_data))
        daily_sign_in_data.rename(columns={'source':'user_id', 'reward':'sign_in_reward'}, inplace=True)
        daily_sign_in_data['date'] = daily_sign_in_data['date'].apply(self.time_offset)

        sign_in_sum = daily_sign_in_data.groupby(['user_id', 'date'])['sign_in_reward'].sum()
        sign_in_sum = sign_in_sum.reset_index()
        return sign_in_sum

    def get_users_pay_data(self, start_date, end_date):
        users_pays_data = mongo.third_pay.find(
            {'pay_date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)}},
            {'source':1, 'price':1, '_id':0, 'pay_date':1}
        )
        daily_pay_data = pandas.DataFrame(list(users_pays_data))
        daily_pay_data.rename(columns={'source':'user_id', 'pay_date':'date'}, inplace=True)
        daily_pay_data['price'] = daily_pay_data['price'].apply(lambda x:x/100)
        daily_pay_data['date'] = daily_pay_data['date'].apply(self.time_offset)
        pay_sum_data = daily_pay_data.groupby(['user_id', 'date'])['price'].sum()
        pay_sum_data = pay_sum_data.reset_index()

        return pay_sum_data

    # def get_gift_log(self, start_date, end_date):
        # gift_log = mongo.gift_log.find(
        #     {'date': {'$gte': datetime.datetime(start_date[0], start_date[1], start_date[2], start_date[3], 0),
        #               '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}},
        #     {'date': 1, 'source': 1, '_id': 0, 'gift.price': 1})
        # temp = []
        # for i in gift_log:
        #     if len(temp) > 0 and len(temp) %50000 == 0:
        #         gift_data = pandas.DataFrame(temp)
        #         gift_data['send_gift'] = gift_data['gift'].apply(lambda x: x['price'])
        #         gift_data.rename(columns={'source': 'user_id'}, inplace=True)
        #         gift_data['date'] = gift_data['date'].apply(lambda x: str(x).split()[0])
        #         gift_data.to_csv('lottery_data/gift_log.csv', mode='a')
        #         del temp
        #         temp = []
        #     temp.append(i)
        # exit()

        # gift_data['send_gift'] = gift_data['gift'].apply(lambda x:x['price'])
        # gift_data.rename(columns={'source':'user_id'}, inplace=True)
        # gift_data['date'] = gift_data['date'].apply(lambda x:str(x).split()[0])
        # gift_sum_data = gift_data.groupby(by=['user_id', 'date'])['send_gift'].sum()
        # gift_sum_data = gift_sum_data.reset_index()
        # gift_sum_data.to_csv('lottery_data/gift_log.csv')

    def time_offset(self, group):
        group = group + pandas.tseries.offsets.Hour(8)
        return datetime.datetime(group.year, group.month, group.day)

    def daily_reward_analysis(self, users_lottery_data, require_list):
        print('获取抽奖数据')
        users_lottery_df = pandas.DataFrame(users_lottery_data)
        users_lottery_df.rename(columns={'source': 'user_id'}, inplace=True)

        # users_lottery_df['date'] = users_lottery_df['date'].apply(lambda x: str(x).split(' ')[0])
        users_lottery_df['date'] = users_lottery_df['date'].apply(self.time_offset)
        users_lottery_df['lottery_award'] = users_lottery_df['lottery_award'].apply(lambda x: x['reward'])
        users_lottery_df['lottery_times'] = 1

        lottery_data = users_lottery_df.groupby(['user_id', 'date'])['lottery_award', 'lottery_times'].sum()
        merged_data = lottery_data.reset_index()
        # 获取每日任务数据
        if 'task' in require_list:
            print('与每日任务合并')
            daily_task_data = self.get_users_task_reward_data(start_date, end_date)
            merged_data = merged_data.merge(daily_task_data, on=['user_id', 'date'], how='outer').fillna(0)
        # print(merged_data.lottery_award.sum())
        if 'online' in require_list:
            print('与每日在线领奖合并')
            daily_online_reward_data = self.get_users_online_reward_data(start_date, end_date)
            merged_data = merged_data.merge(daily_online_reward_data, on=['user_id', 'date'], how='outer').fillna(0)
            merged_data.fillna(0)
        if 'sign_in' in require_list:
            print('与每日签到合并')
            daily_sign_in_data = self.get_users_sign_in_data(start_date, end_date)
            merged_data = merged_data.merge(daily_sign_in_data, on=['user_id', 'date'], how='outer').fillna(0)
            merged_data.fillna(0)
        if 'pay' in require_list:
            print('与每日充值合并')
            daily_pay_data = self.get_users_pay_data(start_date, end_date)
            merged_data = merged_data.merge(daily_pay_data, on=['user_id', 'date'], how='outer').fillna(0)
            merged_data.fillna(0)
        if 'gift' in require_list:
            print('与每日送礼合并')
            daily_send_gift_data = pandas.read_csv('lottery_data/gift_sum_log.csv')
            merged_data = merged_data.merge(daily_send_gift_data, on=['user_id', 'date'], how='outer').fillna(0)
            merged_data.fillna(0)

        print('与用户表合并')
        # 与用户表合并，增加nick_name列
        all_users = self.get_users()
        merged_data = merged_data.merge(all_users, on=['user_id'])

        print('写入csv中')
        merged_data.to_csv('lottery_data/lottery_data{}-{}.csv'.format(start_date.day, end_date.day))

    def get_users(self):
        all_users = mongo.all_users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}}, {'channel':1,'user_info.nickname':1, 'regist_date':1})
        all_user = pandas.DataFrame(list(all_users))
        all_user.rename(columns={'user_info': 'name', '_id': 'user_id'}, inplace=True)
        all_user['name'] = all_user['name'].apply(lambda x: x['nickname'])
        all_user['user_id'] = all_user['user_id'].apply(lambda x: str(x))
        all_user['regist_date'] = all_user['regist_date'].apply(self.time_offset)
        # all_user['regist_date'] = all_user['regist_date'].apply(lambda x:datetime.datetime(x.year,x.month,x.day))
        return all_user

    def get_lottery_award(self, start_date, end_date):
        lottery_log = mongo.lottery_log.aggregate(
            [
                {'$match': {'date': {'$gte': start_date - datetime.timedelta(hours=8),
                      '$lte': end_date - datetime.timedelta(hours=8)}}},
                {'$group': {'_id': '$source', 'lottery_times': {'$sum': 1}, 'lottery_award':{'$sum':'$lottery_award.reward'}}}
            ]
        )

        return list(lottery_log)


if __name__ == '__main__':
    mongo = Mongo()
    start_date, end_date = datetime.datetime(*[2018,9,1, 0,0]), datetime.datetime(*[2018,9,3,0,0])
    ull = UserLotteryLog()
    users_lottery_data = ull.get_users_lottery_data(start_date, end_date)
    require_list = ['task', 'online', 'sign_in', 'pay']
    ull.daily_reward_analysis(users_lottery_data,require_list)

    lottery_award_data = ull.get_lottery_award(start_date, end_date)
    ldf = pandas.DataFrame(lottery_award_data)
    print(ldf.lottery_award.sum())
    print(ldf.lottery_times.sum())