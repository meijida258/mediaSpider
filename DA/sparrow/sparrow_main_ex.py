import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from sparrow.daily_analysis import Analysis as daily_Analysis
from sparrow.daily_analysis import AnalysisTools as Analysis_Tools

# 过滤数据脚本
from pymongo import MongoClient
import time, datetime, requests
import pandas, numpy

import cProfile, pstats

data_file_save_path = 'D:/sparrow_data'


url_headers = {'Authorization':'Token 8103598e41ea781aaa1567e8c44ec50e84b2bc5fc6f8f4e696eb2e49ad188f4d',
              'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.sparrow_main

        self.coin_trader_db = self.client.sparrow_coin_trader

        self.db2 = self.client.sparrow_analysis
        # 所有数据源文件
        self.agent_recharge_log = self.db.agent_recharge_log
        self.apple_iap_log = self.db.apple_iap_log
        self.apple_iap_opt = self.db.apple_iap_opt
        self.beginner_cards = self.db.beginner_cards
        self.beginner_card_log = self.db.beginner_card_log
        self.complaints = self.db.complaints
        self.contacts = self.db.contacts
        self.daily_tasks = self.db.daily_tasks
        self.daily_task_log = self.db.daily_task_log
        self.extension_log = self.db.extension_log
        self.first_recharge_log = self.db.first_recharge_log
        self.gifts = self.db.gifts
        self.gift_log = self.db.gift_log
        self.global_vars = self.db.global_vars
        self.guardians = self.db.guardians
        self.guard_log = self.db.guard_log
        self.guard_opt = self.db.guard_opt
        self.login_log = self.db.login_log
        self.online_amount_log = self.db.online_amount_log
        self.online_reward_log = self.db.online_reward_log
        self.private_messages = self.db.private_messages
        self.promotions = self.db.promotions
        self.proposals = self.db.proposals
        self.realname_requests = self.db.realname_requests
        self.recharge_opt = self.db.recharge_opt
        self.recharge_orders = self.db.recharge_orders
        self.room_log = self.db.room_log
        self.settlement_orders = self.db.settlement_orders
        self.share_app_log = self.db.share_app_log
        self.sign_in_log = self.db.sign_in_log
        self.sign_in_reward = self.db.sign_in_reward
        self.store_items = self.db.store_items
        self.store_orders = self.db.store_orders
        self.users = self.db.users
        self.user_tags = self.db.user_tags
        self.player_recharge_from_coin_trader_log = self.coin_trader_db.player_recharge_log
        # 保存筛选后的数据集
        self.users_data = self.db2.users_date_data
        self.game_daily_log = self.db2.game_daily_log
        self.users_daily_log = self.db2.users_daily_log


    def data_remove(self):
        self.users_data.remove()


class Analysis:
    # 先获得不是机器人的用户
    def get_users(self):
        # users = mongo.users.find({'$or':[{'username':{'$regex':r'.{28}'}}, {'username':{'$regex':r'\d{11}'}}]})
        users = mongo.users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}, 'regist_date':{'$lte':datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}})
        return users


    def main(self, offset_day, insert=True):
        # 过滤机器人，记录其他人的用户名和登录时间
        self.offset_day = offset_day
        self.time_today = time.time()
        self.st_year, self.st_month, self.st_day = int(
            time.strftime('%Y', time.localtime(self.time_today - 86400 * (self.offset_day + 2)))), int(
            time.strftime('%m', time.localtime(self.time_today - 86400 * (self.offset_day + 2)))), int(
            time.strftime('%d', time.localtime(self.time_today - 86400 * (self.offset_day + 2))))
        self.end_year, self.end_month, self.end_day = int(
            time.strftime('%Y', time.localtime(self.time_today - 86400 * (self.offset_day + 1)))), int(
            time.strftime('%m', time.localtime(self.time_today - 86400 * (self.offset_day + 1)))), int(
            time.strftime('%d', time.localtime(self.time_today - 86400 * (self.offset_day + 1))))
        self.save_date = time.strftime('%Y-%m-%d', time.localtime(self.time_today - 86400 * (self.offset_day + 1)))
        print('查找%s' %str(self.save_date))
        # exit()
        self.start_timestamp = int(time.mktime((self.end_year, self.end_month, self.end_day, 4, 0, 0, 0, 0, 0)))
        self.finish_timestamp = int(time.mktime((self.end_year, self.end_month, self.end_day + 1, 4, 0, 0, 0, 0, 0)))

        # 用户基础数据
        users_data = self.get_users()
        # 用户行为数据, 均为DataFrame格式
        # 支付
        third_pay_log_data, apple_pay_log_data, coin_trader_pay_log_data = self.get_users_pay_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                                                                                  end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 游戏
        ext_log_data = self.get_users_ext_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 任务
        task_log_data = self.get_users_task_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 签到
        sign_in_reward_data = self.get_users_sign_in_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 在线
        online_reward_data = self.get_users_online_reward_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 礼物
        # 送
        normal_gift_log_data, special_gift_log_data = self.get_users_gift_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 收
        receive_normal_gift_log_data, receive_special_gift_log_data = self.get_users_receive_gift_log(st_date=[self.st_year, self.st_month, self.st_day, 20, 0],
                                            end_date=[self.end_year, self.end_month, self.end_day, 20, 0])
        # 非机器人的游戏数据
        users_game_data = {}
        users_game_data['new_user_play_count'], users_game_data['new_user_play_amount'] = [0]*5, [0]*5
        users_game_data['old_user_play_count'], users_game_data['old_user_play_amount'] = [0]*5, [0]*5
        users_game_data['save_time'] = self.save_date
        for user_data in users_data:
            save_data = {}
            save_data['user_id'] = str(user_data['_id'])
            save_data['username'] = user_data['username']
            save_data['login_date'] = user_data['login_date']
            save_data['regist_date'] = user_data['regist_date']
            save_data['level'] = user_data['user_info']['level']
            save_data['nickname'] = user_data['user_info']['nickname']
            save_data['gift_purchase'] = user_data['statistic']['gift_purchase']
            save_data['money'] = user_data['money']
            if user_data['channel']:
                save_data['channel'] = user_data['channel']
            else:
                save_data['channel'] = '官方'
            save_data['save_time'] = self.save_date
            # 通过save_data中的用户名查询当天的充值情况
            print('查询%s的行为数据' % save_data['user_id'])
            save_data = self.add_data_to_dict(source_data=third_pay_log_data, save_dict=save_data, source_keys=['pay_count', 'pay_amount'], save_keys=['third_pay_count', 'third_pay_amount'])
            save_data = self.add_data_to_dict(source_data=apple_pay_log_data, save_dict=save_data, source_keys=['pay_count', 'pay_amount'], save_keys=['apple_pay_count', 'apple_pay_amount'])
            save_data = self.add_data_to_dict(source_data=coin_trader_pay_log_data, save_dict=save_data, source_keys=['pay_count', 'pay_amount'], save_keys=['coin_trader_pay_count', 'coin_trader_pay_amount'])
            # 查询当天的任务领取情况
            save_data = self.add_data_to_dict(source_data=task_log_data, save_dict=save_data, source_keys=['finish_task_count', 'task_reward'], save_keys=['finish_task_count', 'task_reward'])
            # 查询当天的打赏情况
            save_data = self.add_data_to_dict(source_data=normal_gift_log_data, save_dict=save_data, source_keys=['send_gift_count', 'send_gift_amount'], save_keys=['send_normal_gift_count', 'send_normal_gift_amount'])
            save_data = self.add_data_to_dict(source_data=special_gift_log_data, save_dict=save_data, source_keys=['send_gift_count', 'send_gift_amount'], save_keys=['send_special_gift_count', 'send_special_gift_amount'])
            # 收礼
            save_data = self.add_data_to_dict(source_data=receive_normal_gift_log_data, save_dict=save_data,
                                              source_keys=['receive_gift_count', 'receive_gift_amount'],
                                              save_keys=['receive_normal_gift_count', 'receive_normal_gift_amount'])
            save_data = self.add_data_to_dict(source_data=receive_special_gift_log_data, save_dict=save_data,
                                              source_keys=['receive_gift_count', 'receive_gift_amount'],
                                              save_keys=['receive_special_gift_count', 'receive_special_gift_amount'])
            # 查询当天的在线领取、签到情况
            save_data = self.add_data_to_dict(source_data=online_reward_data, save_dict=save_data, source_keys=['reward_count', 'reward_amount'], save_keys=['online_count', 'online_reward'])
            save_data = self.add_data_to_dict(source_data=sign_in_reward_data, save_dict=save_data, source_keys=['sign_in_days', 'sign_in_reward'], save_keys=['sign_in_days', 'sign_in_reward'])
            # 查询当天游戏记录
            save_data = self.add_data_to_dict(source_data=ext_log_data, save_dict=save_data, source_keys=['play_count', 'play_amount'], save_keys=['play_count', 'play_amount'])

            if insert:
                if mongo.users_daily_log.find({'save_time':save_data['save_time'], 'user_id':save_data['user_id']}).count() == 0:
                    mongo.users_daily_log.insert(save_data)
            else:
                return save_data

            # 记录非机器人的游戏数据
            user_game_data = list(mongo.extension_log.aggregate(
                [
                    {'$match':{'user_id':save_data['user_id'], 'date':{'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0),
                                 '$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                    {'$group':{'_id':'$user_id', 'ext_id':{'$push':'$ext_id'}, 'consume':{'$push':'$consume'}}}
                ]
            ))
            if user_game_data:
                ext_id_list = user_game_data[0]['ext_id']
                consume_list = user_game_data[0]['consume']
                for x, y in zip(ext_id_list, consume_list):
                    if analy_tool.datetime_to_timestamp(str(datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0))) >= analy_tool.datetime_to_timestamp(str(save_data['regist_date']).split('.')[0]) >= analy_tool.datetime_to_timestamp(str(datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0))):
                        users_game_data['new_user_play_count'][x-1] += 1
                        users_game_data['new_user_play_amount'][x-1] += y
                    else:
                        users_game_data['old_user_play_count'][x - 1] += 1
                        users_game_data['old_user_play_amount'][x - 1] += y
        if mongo.game_daily_log.find({'save_time':self.save_date}).count() == 0:
            mongo.game_daily_log.insert(users_game_data)
    def add_data_to_dict(self, source_data, save_dict, source_keys, save_keys):
        if not source_data.empty:
            target_data = source_data[source_data['_id']==save_dict['user_id']]
            for key in source_keys:
                if not target_data.empty:
                    save_dict[save_keys[source_keys.index(key)]] = target_data.ix[target_data.index[0], key] if not isinstance(target_data.ix[target_data.index[0], key], numpy.int64) else int(target_data.ix[target_data.index[0], key])
                else:
                    save_dict[save_keys[source_keys.index(key)]] = 0
        else:
            for key in source_keys:
                save_dict[save_keys[source_keys.index(key)]] = 0
        return save_dict

    # --------------------------------------
    # 支付
    def get_users_pay_log(self, st_date, end_date):
        # 三方支付
        third_pay_log = mongo.recharge_orders.aggregate([
            {'$match':{'pay_date':{'$gte':datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                                  '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group':{'_id':'$source','pay_count':{'$sum':1}, 'pay_amount':{'$sum':'$amount'}}}
        ])
        third_pay_log_data = {'_id': [], 'pay_count': [], 'pay_amount': []}
        for each_log in third_pay_log:
            third_pay_log_data['_id'].append(each_log['_id'])
            third_pay_log_data['pay_count'].append(each_log['pay_count'])
            third_pay_log_data['pay_amount'].append(each_log['pay_amount'])
        # 苹果支付
        apple_pay_log = mongo.apple_iap_log.aggregate(
            [
                {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                         '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3],
                                                                   0)}}},
                {'$group': {'_id': '$source', 'pay_count': {'$sum': 1}, 'pay_amount': {'$sum': '$amount'}}}
            ]
        )
        apple_pay_log_data = {'_id': [], 'pay_count': [], 'pay_amount': []}
        for each_log in apple_pay_log:
            apple_pay_log_data['_id'].append(each_log['_id'])
            apple_pay_log_data['pay_count'].append(each_log['pay_count'])
            apple_pay_log_data['pay_amount'].append(each_log['pay_amount'])
        # 银商购买
        coin_trader_pay_log = mongo.recharge_orders.aggregate([
            {'$match':{'date':{'$gte':datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                                  '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group':{'_id':'$target','pay_count':{'$sum':1}, 'pay_amount':{'$sum':'$amount'}}}
        ])
        coin_trader_pay_log_data = {'_id': [], 'pay_count': [], 'pay_amount': []}
        for each_log in coin_trader_pay_log:
            coin_trader_pay_log_data['_id'].append(each_log['_id'])
            coin_trader_pay_log_data['pay_count'].append(each_log['pay_count'])
            coin_trader_pay_log_data['pay_amount'].append(each_log['pay_amount'])
        return pandas.DataFrame(third_pay_log_data), pandas.DataFrame(apple_pay_log_data), pandas.DataFrame(coin_trader_pay_log_data)
    # 任务
    def get_users_task_log(self, st_date, end_date):
        task_log = mongo.daily_task_log.aggregate(
            [
                {'$match':{'date':{'$gte':datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                   '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
                {'$group':{'_id':'$source', 'finish_task_count':{'$sum':1}, 'task_reward':{'$sum':'$reward'}}}
            ]
        )
        task_log_data = {'_id': [], 'finish_task_count': [], 'task_reward': []}
        for each_log in task_log:
            task_log_data['_id'].append(each_log['_id'])
            task_log_data['finish_task_count'].append(each_log['finish_task_count'])
            task_log_data['task_reward'].append(each_log['task_reward'])
        return pandas.DataFrame(task_log_data)

    # 游戏
    def get_users_ext_log(self, st_date, end_date):
        ext_log = mongo.extension_log.aggregate([
            {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                 '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group': {'_id': '$user_id', 'play_count': {'$sum': 1}, 'play_amount': {'$sum': '$consume'}}}
        ])
        ext_log_data = {'_id': [], 'play_count': [], 'play_amount': []}
        for each_log in ext_log:
            ext_log_data['_id'].append(each_log['_id'])
            ext_log_data['play_count'].append(each_log['play_count'])
            ext_log_data['play_amount'].append(each_log['play_amount'])
        return pandas.DataFrame(ext_log_data)
    # 送礼物
    def get_users_gift_log(self, st_date, end_date):
        normal_gift_log = mongo.gift_log.aggregate([
            {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                 '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)},
                        'gift.special':False}},
            {'$group': {'_id': '$source', 'send_gift_count': {'$sum': 1}, 'send_gift_amount': {'$sum': '$gift.price'}}}
        ])
        normal_gift_log_data = {'_id': [], 'send_gift_count': [], 'send_gift_amount': []}
        for each_log in normal_gift_log:
            normal_gift_log_data['_id'].append(each_log['_id'])
            normal_gift_log_data['send_gift_count'].append(each_log['send_gift_count'])
            normal_gift_log_data['send_gift_amount'].append(each_log['send_gift_amount'])

        special_gift_log = mongo.gift_log.aggregate([
            {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                 '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)},
                        'gift.special':True}},
            {'$group': {'_id': '$source', 'send_gift_count': {'$sum': 1}, 'send_gift_amount': {'$sum': '$gift.price'}}}
        ])
        special_gift_log_data = {'_id': [], 'send_gift_count': [], 'send_gift_amount': []}
        for each_log in special_gift_log:
            special_gift_log_data['_id'].append(each_log['_id'])
            special_gift_log_data['send_gift_count'].append(each_log['send_gift_count'])
            special_gift_log_data['send_gift_amount'].append(each_log['send_gift_amount'])
        return pandas.DataFrame(normal_gift_log_data), pandas.DataFrame(special_gift_log_data)

        # 手礼物
    def get_users_receive_gift_log(self, st_date, end_date):
        normal_gift_log = mongo.gift_log.aggregate([
                {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)},
                            'gift.special': False}},
                {'$group': {'_id': '$target', 'receive_gift_count': {'$sum': 1},
                            'receive_gift_amount': {'$sum': '$gift.price'}}}
            ])
        normal_gift_log_data = {'_id': [], 'receive_gift_count': [], 'receive_gift_amount': []}
        for each_log in normal_gift_log:
            normal_gift_log_data['_id'].append(each_log['_id'])
            normal_gift_log_data['receive_gift_count'].append(each_log['receive_gift_count'])
            normal_gift_log_data['receive_gift_amount'].append(each_log['receive_gift_amount'])

        special_gift_log = mongo.gift_log.aggregate([
                {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)},
                            'gift.special': True}},
                {'$group': {'_id': '$target', 'receive_gift_count': {'$sum': 1},
                            'receive_gift_amount': {'$sum': '$gift.price'}}}
            ])
        special_gift_log_data = {'_id': [], 'receive_gift_count': [], 'receive_gift_amount': []}
        for each_log in special_gift_log:
            special_gift_log_data['_id'].append(each_log['_id'])
            special_gift_log_data['receive_gift_count'].append(each_log['receive_gift_count'])
            special_gift_log_data['receive_gift_amount'].append(each_log['receive_gift_amount'])
        return pandas.DataFrame(normal_gift_log_data), pandas.DataFrame(special_gift_log_data)
    # 签到
    def get_users_sign_in_log(self, st_date, end_date):
        sign_in_log = mongo.sign_in_log.aggregate([
            {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                 '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group': {'_id': '$source', 'sign_in_days': {'$sum': '$days'}, 'sign_in_reward': {'$sum': '$reward'}}}
        ])
        sign_in_log_data = {'_id': [], 'sign_in_days': [], 'sign_in_reward': []}
        for each_log in sign_in_log:
            sign_in_log_data['_id'].append(each_log['_id'])
            sign_in_log_data['sign_in_days'].append(each_log['sign_in_days'])
            sign_in_log_data['sign_in_reward'].append(each_log['sign_in_reward'])
        return pandas.DataFrame(sign_in_log_data)

    # 在线
    def get_users_online_reward_log(self, st_date, end_date):
        online_reward_log = mongo.online_reward_log.aggregate([
            {'$match': {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                 '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group': {'_id': '$source', 'reward_count': {'$sum': 1}, 'reward_amount': {'$sum': '$reward'}}}
        ])
        online_reward_log_data = {'_id': [], 'reward_count': [], 'reward_amount': []}
        for each_log in online_reward_log:
            online_reward_log_data['_id'].append(each_log['_id'])
            online_reward_log_data['reward_count'].append(each_log['reward_count'])
            online_reward_log_data['reward_amount'].append(each_log['reward_amount'])
        return pandas.DataFrame(online_reward_log_data)

if __name__ == '__main__':
    # import pymongo
    mongo = Mongo()
    analy = Analysis()
    daily_aly = daily_Analysis()
    analy_tool = Analysis_Tools()
    #54开始

    for off_day in range(66, 70):
        st_time = time.time()
        # analy.main(off_day)
        # cProfile.run("analy.main(off_day)")
        analy.main(off_day)
        # daily_aly.main(off_day)
        print(time.time() - st_time)
    start_time = time.time()


else:
    mongo = Mongo()
    analy = Analysis()