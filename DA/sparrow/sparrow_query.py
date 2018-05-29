import sys
import os

PACKAGE_PARENT = '.'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

# 过滤数据脚本
from pymongo import MongoClient
import time, datetime, requests
from multiprocessing.dummy import Pool
from daily_analysis import Analysis as daily_Analysis
from daily_analysis import AnalysisTools as Analysis_Tool
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
        self.game_data = self.db2.daily_game_log
        self.users_data_log = self.db2.users_log
        # 测试用
        self.temp_log = self.db2.temp_users_log


    def data_remove(self):
        self.users_data.remove()
        self.game_data.remove()

class Analysis:
    # def __init__(self):
    #     # self.offset_day = 10



    # 先获得不是机器人的用户
    def get_users(self):
        # users = mongo.users.find({'$or':[{'username':{'$regex':r'.{28}'}}, {'username':{'$regex':r'\d{11}'}}]})
        users = mongo.users.find({'username':{'$regex':r'^(?!robot_[0-9]{5})'}})
        return users

    def get_user_game_data(self, user_id, start_time, finish_time):
        while True:
            try:
                game_data_json = requests.get('https://www.maquetv.com:8080/admin/extension_log',
                                   params={'target':user_id,
                                           'start':start_time,
                                           'finish':finish_time},
                                   headers = url_headers).json()
                return game_data_json
            except:
                print('获取%s游戏数据出错' %user_id)

    # 游戏记录查询
    def get_user_game_log(self, user_data, start_timestamp, finish_timestamp):
        user_id = user_data['user_id']
        print('查询%s游戏记录' %user_id)
        game_data_json = self.get_user_game_data(user_id, start_time=start_timestamp, finish_time=finish_timestamp)
        user_data['ext_count'] = 0
        user_data['ext_consume'] = 0
        if game_data_json['total'] > 0:
            user_data['ext_count'] = game_data_json['total']
            for each_ext_log in game_data_json['ext']:
                user_data['ext_consume'] += each_ext_log['consume']
                # 游戏记录存入本地
                game_ext_id = user_id + str(each_ext_log['date'])
                if mongo.game_data.find({'game_ext_id':game_ext_id}).count() == 0:
                    each_ext_log['game_ext_id'] = game_ext_id
                    mongo.game_data.insert(each_ext_log)
        return user_data
        # user_game_data = mongo.extension_log({'username':user_id, 'date':{'$get':}})

    # 支付查询
    def get_user_pay_log(self, user_data, st_date, end_date):
        user_id = str(user_data['user_id'])
        print('查询%s支付记录' %user_id)
        # 查询苹果支付
        apple_pay_log = mongo.apple_iap_log.find({'$and':[{'source':user_id},{
            'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}]})
        user_data['apple_pay_amount'] = 0
        if apple_pay_log.count() > 0:
            user_data['apple_pay_count'] = apple_pay_log.count()
            for each_log in apple_pay_log:
                user_data['apple_pay_amount'] += each_log['price']
        else:
            user_data['apple_pay_count'] = 0
        # 查询第三方支付
        third_pay_log = mongo.recharge_orders.find({'$and':[{'source':user_id},{
            'pay_date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}]})
        user_data['third_pay_amount'] = 0
        if third_pay_log.count() > 0:
            user_data['third_pay_count'] = third_pay_log.count()
            for each_log in third_pay_log:
                user_data['third_pay_amount'] += each_log['amount']
        else:
            user_data['third_pay_count'] = 0
        # 查询银商购买
        coin_trader_log = mongo.player_recharge_from_coin_trader_log.find({'$and':[{'target':user_id},{
            'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}]})
        user_data['coin_trader_amount'] = 0
        if coin_trader_log.count() > 0:
            user_data['coin_trader_count'] = coin_trader_log.count()
            sell_trader = []
            for each_log in coin_trader_log:
                user_data['coin_trader_amount'] += each_log['amount']
                if sell_trader.count(each_log['source']) == 0:
                    sell_trader.append(each_log['source'])
            user_data['coin_trader_list'] = sell_trader[:]
        else:
            user_data['coin_trader_count'] = 0
        print('%s查询到苹果支付：%s条，三方支付：%s条，银商购买：%s条' %(user_data['user_id'], str(apple_pay_log.count()),
                                                  str(third_pay_log.count()), str(coin_trader_log.count())))
        return user_data

    # 任务查询
    def get_user_task_log(self, user_data, st_date, end_date):
        user_id = user_data['user_id']
        print('查询%s任务记录' %user_id)
        user_task_log = mongo.daily_task_log.find({'$and':[{'source':user_id}, {'date':{'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], 20, 0),
                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 20, 0)}}]})

        user_data['task_reward'] = 0
        if user_task_log.count() > 0:
            user_data['task_count'] = user_task_log.count()
            for each_log in user_task_log:
                user_data['task_reward'] += each_log['reward']
        else:
            user_data['task_count'] = 0

        return user_data

    # 打赏、收礼查询
    def get_user_gift_log(self, user_data, st_date, end_date):
        user_id = user_data['user_id']
        print('查询%s打赏、收礼记录' %user_id)
        user_gift_log = mongo.gift_log.find({'$and':[{'$or':[{'source':user_id}, {'target':user_id}]},
                                                     {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], 20, 0),
                                                               '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 20, 0)}}]})
        user_data['send_gift_count'], user_data['send_gift_amount'] = 0, 0
        user_data['receive_gift_count'], user_data['receive_gift_amount'] = 0, 0
        user_data['send_special_gift_count'], user_data['send_special_gift_amount'] = 0, 0
        user_data['receive_special_gift_count'], user_data['receive_special_gift_amount'] = 0, 0
        if user_gift_log.count() > 0:
            for each_log in user_gift_log:
                if each_log['source'] == user_id:
                    if each_log['gift']['special']:
                        user_data['send_special_gift_count'] += 1
                        user_data['send_special_gift_amount'] += each_log['gift']['price']
                    else:
                        user_data['send_gift_count'] += 1
                        user_data['send_gift_amount'] += each_log['gift']['price']
                else:
                    if each_log['gift']['special']:
                        user_data['receive_special_gift_count'] += 1
                        user_data['receive_special_gift_amount'] += each_log['gift']['price']
                    else:
                        user_data['receive_gift_count'] += 1
                        user_data['receive_gift_amount'] += each_log['gift']['price']
        return user_data

    # 签到、在线领取查询
    def get_user_other_reward_log(self, user_data, st_date, end_date):
        user_id = user_data['user_id']
        print('查询%s签到、在线领取记录' %user_id)
        user_online_reward_log = mongo.online_reward_log.find({'$and':[{'source':user_id},
                                                     {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], 20, 0),
                                                               '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 20, 0)}}]})
        if user_online_reward_log.count() > 0:
            user_data['online_reward'] = user_online_reward_log.count() * 10
        else:
            user_data['online_reward'] = 0

        user_sign_in_reward_log = mongo.sign_in_log.find({'$and':[{'source':user_id},
                                                     {'date': {'$gte': datetime.datetime(st_date[0], st_date[1], st_date[2], 20, 0),
                                                               '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 20, 0)}}]})
        if user_sign_in_reward_log.count() > 0:
            user_data['sign_in_reward'] = user_sign_in_reward_log[0]['reward']
            user_data['sign_in_days'] = user_sign_in_reward_log[0]['days']
        else:
            user_data['sign_in_reward'] = 0
            user_data['sign_in_days'] = 0
        return user_data

    def main(self, offset_day):
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

        #
        users_data = self.get_users()

        pool = Pool(4)
        pool.map(self.threading_control, users_data)
        pool.close()
        pool.join()


    def threading_control(self, user_data, st_date=None, end_date=None, start_timestamp=None, finish_timestamp=None, insert=True):
        # 设置查询时间
        if not st_date:
            st_date = [self.st_year, self.st_month, self.st_day, 20]
        if not end_date:
            end_date = [self.end_year, self.end_month, self.end_day, 20]
        if not start_timestamp:
            start_timestamp = self.start_timestamp
        if not finish_timestamp:
            finish_timestamp = self.finish_timestamp
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
        save_data = self.get_user_pay_log(save_data, st_date=st_date, end_date=end_date)
        # 查询当天的任务领取情况
        save_data = self.get_user_task_log(save_data, st_date=st_date, end_date=end_date)
        # 查询当天的打赏、收礼情况
        save_data = self.get_user_gift_log(save_data, st_date=st_date, end_date=end_date)
        # 查询当天的在线领取、签到情况
        save_data = self.get_user_other_reward_log(save_data, st_date=st_date, end_date=end_date)
        # 查询当天游戏记录
        save_data = self.get_user_game_log(save_data, start_timestamp=start_timestamp, finish_timestamp=finish_timestamp)
        if insert:
            mongo.temp_log.insert(save_data)
            # if mongo.users_data_log.find({'save_time':save_data['save_time'], 'user_id':save_data['user_id']}).count() == 0:
            #     mongo.users_data_log.insert(save_data)
        else:
            return save_data
        # 查询用户的游戏消费
        print('--------------')

    def get_user_pay_ex(self, user_data, st_date, end_date):
        user_id = user_data['user_id']
        third_pay = mongo.recharge_orders.aggregate([
            {'$match':{'pay_date':{'$gte':datetime.datetime(st_date[0], st_date[1], st_date[2], st_date[3], 0),
                                                  '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], end_date[3], 0)}}},
            {'$group':{'_id':'$source','pay_count':{'$sum':1}, 'pay_amount':{'$sum':'$amount'}}}
        ])
        result = list(third_pay)
        return result
if __name__ == '__main__':
    mongo = Mongo()
    analy = Analysis()
    daily_aly = daily_Analysis()
    analy_tool = Analysis_Tool()
    for off_day in range(10, 11):
        # mongo.data_remove()
        st_time = time.time()
        analy.main(off_day)
        # daily_aly.main(off_day)
        print(time.time() - st_time)
    # start_time = time.time()
    # # 查时间段类所有用户
    #
    # user_data = {'user_id':'5a7f8dac8ea6a005e53bc0cc'}
    # # result = analy.get_user_pay_log(user_data=user_data, st_date=[2018,2,20,0,0], end_date=[2018,2,24,0,0])
    # result = analy.get_user_pay_ex(user_data=user_data, st_date=[2018,2,20,0,0], end_date=[2018,2,24,0,0])
    #
    # print(result)
    # print(time.time()-start_time)
else:
    mongo = Mongo()
    analy = Analysis()