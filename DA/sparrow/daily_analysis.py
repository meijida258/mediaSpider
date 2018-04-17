# 分析每天数据
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy, pandas
import time, csv, os, datetime
from bson.objectid import ObjectId


all_users_keys = ['gift_purchase', 'apple_pay_amount', 'sign_in_reward', 'play_count', 'task_reward', 'send_normal_gift_amount', 'save_time', 'nickname', 'finish_task_count', 'regist_date', 'login_date', 'receive_normal_gift_count', 'channel', 'online_count', 'play_amount', 'send_normal_gift_count', 'receive_normal_gift_amount', 'money', 'level', 'third_pay_count', 'online_reward', 'username', 'user_id', 'apple_pay_count', 'sign_in_days', 'third_pay_amount']

daily_data = {}

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        # 过滤后的数据集
        self.db = self.client.sparrow_analysis
        self.users_data = self.db.users_date_data
        self.game_daily_log = self.db.game_daily_log
        self.daily_data = self.db.daily_deal_data
        self.users_daily_log = self.db.users_daily_log
        # 主数据集
        self.db2 = self.client.sparrow_main
        self.beginner_card_log = self.db2.beginner_card_log
        self.users = self.db2.users
        self.ext_log = self.db2.extension_log
        self.recharge_orders = self.db2.recharge_orders
        self.apple_iap_log = self.db2.apple_iap_log

class Analysis:

    def user_filter(self):
        users_data = mongo.users_daily_log.find({'save_time':self.save_date,'$or':[{'play_count':{'$gt':0}},
                                                   {'sign_in_reward':{'$gt':0}},
                                                   {'finish_task_count':{'$gt':0}},
                                                   {'login_date':{'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0),
                                                               '$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}},
                                                   {'coin_trader_pay_count':{'$gt':0}},
                                                   {'apple_pay_count':{'$gt':0}},
                                                   {'third_pay_count':{'$gt':0}},
                                                   {'send_special_gift_count': {'$gt':0}},
                                                   {'send_normal_gift_count': {'$gt': 0}},
                                                   {'receive_special_gift_count': {'$gt': 0}},
                                                   {'receive_normal_gift_count': {'$gt': 0}}]})
        return users_data

    def all_users(self):
        save_path = self.data_file_save_path+'/all_users.csv'
        if os.path.exists(save_path):
            return
        else:
            users_data = mongo.users_daily_log.find({'save_time':self.save_date})
            at.write_csv(file_path=save_path, head=all_users_keys, data=users_data, keys=all_users_keys)

    def get_new_regist_user_id(self):
        new_regist_mongo = mongo.users.aggregate(
            [
                {'$match':{'regist_date':{'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0),
                                                                '$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                {'$group':{'_id':'$_id'}}
            ]
        )
        new_regist_list = []
        for each_new_regist in new_regist_mongo:
            new_regist_list.append(str(each_new_regist['_id']))
        return new_regist_list

    def get_robot_user_id(self):
        robot_mongo = mongo.users.aggregate(
            [
                {'$match':{'username':{'$regex':r'(robot_[0-9]{5})'}}},
                {'$group':{'_id':'$_id'}}
            ]
        )
        robot_list = []
        for each_robot in robot_mongo:
            robot_list.append(str(each_robot['_id']))
        return robot_list

    # 获取在线用户数据
    def get_dau_data(self):
        csv_content = pandas.read_csv(self.data_file_save_path + '/' + 'dau.csv')
        rows = csv_content.shape[0]
        new_user = [0] * 5
        old_user = [0] * 5
        # [登录， 游戏， 充值， 消费， 任务]
        activate_users_data = mongo.users_daily_log.aggregate(
            [
                {'$match':{'save_time':self.save_date, }}
            ]
        )
        for each_row in range(0, rows):
            if at.datetime_to_timestamp(str(datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0))) >= \
                    at.datetime_to_timestamp(csv_content.ix[each_row, 'regist_date'].split('.')[0]) >= \
                    at.datetime_to_timestamp(str(datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0))):
                new_user[0] += 1
                if csv_content.ix[each_row, 'play_count'] > 0:
                    new_user[1] += 1
                if  csv_content.ix[
                    each_row, 'apple_pay_count'] > 0 or csv_content.ix[each_row, 'third_pay_count'] > 0:
                    new_user[2] += 1
                if  csv_content.ix[
                    each_row, 'send_normal_gift_count'] > 0:
                    new_user[3] += 1
                if csv_content.ix[each_row, 'finish_task_count'] > 0:
                    new_user[4] += 1
            else:
                old_user[0] += 1
                if csv_content.ix[each_row, 'play_count'] > 0:
                    old_user[1] += 1
                if  csv_content.ix[
                    each_row, 'apple_pay_count'] > 0 or \
                                csv_content.ix[each_row, 'third_pay_count'] > 0:
                    old_user[2] += 1
                if  csv_content.ix[
                    each_row, 'send_normal_gift_count'] > 0:
                    old_user[3] += 1
                if csv_content.ix[each_row, 'finish_task_count'] > 0:
                    old_user[4] += 1
        # begin_card_use_count = self.get_begin_card_use_log(
        #         mongo.users.find({'$and': [{'username': {'$regex': r'^(?!robot_[0-9]{5})'}}, {
        #             'regist_date': {'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0),
        #                             '$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}]}))

        return old_user, new_user

    def get_begin_card_use_log(self, users):
        user_count = 0
        for user in users:
            user_count += mongo.beginner_card_log.find({'source':str(user['_id'])}).count()
        return user_count

    # 获取支付数据
    def get_pay_data(self):
        recharge_orders_data = list(mongo.recharge_orders.aggregate(
            [
                {'$match':{'pay_date':{'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0)
                    ,'$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                {'$group':{'_id':'$price','pay_count':{'$sum':1},'pay_amount':{'$sum':'$amount'}, 'user_id':{'$push':'$source'}}}
            ]
        ))
        apple_iap_data = list(mongo.apple_iap_log.aggregate(
            [
                {'$match':{'date':{'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0)
                    ,'$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                {'$group':{'_id':'$price','pay_count':{'$sum':1},'pay_amount':{'$sum':'$amount'}, 'user_id':{'$push':'$source'}}}
            ]
        ))
        return recharge_orders_data + apple_iap_data

    # 获取游戏数据, 新老用户下注次数、豆子
    def get_ext_data(self):
        ext_count = [0] * 5
        ext_consume = [0] * 5
        ext_log = mongo.ext_log.aggregate(
            [
                {'$match': {'date': {'$gte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0)
                    ,'$lte': datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                {'$group': {'_id': '$ext_id', 'play_count': {'$sum': 1}, 'play_amount': {"$sum": '$consume'}}}
            ]
        )
        for each_game_log in ext_log:
            ext_count[each_game_log['_id']-1] = each_game_log['play_count']
            ext_consume[each_game_log['_id'] - 1] = each_game_log['play_amount']
        return ext_count, ext_consume

    # 获取礼物相关数据
    def get_gift_data(self):
        # [[老用户普通礼物个，老用户特殊礼物个],[新用户普通礼物个，新用户特殊礼物个]]
        send_count, send_amount = [[0] * 2, [0]*2], [[0] * 2, [0] * 2]
        new_regist_gift_data = mongo.users_daily_log.aggregate(
            [
                {'$match': {'save_time': self.save_date,
                            'regist_date': {'$gte':datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0),
                                   '$lte':datetime.datetime(self.end_year, self.end_month, self.end_day, 20, 0)}}},
                {'$group': {'_id': '$save_time', 'send_normal_gift_count': {'$sum': '$send_normal_gift_count'},
                            'send_special_gift_count': {'$sum': '$send_special_gift_count'},
                            'send_normal_gift_amount': {'$sum': '$send_normal_gift_amount'},
                            }}
            ]
        )
        old_regist_gift_data = mongo.users_daily_log.aggregate(
            [
                {'$match': {'save_time': self.save_date,
                            'regist_date': {
                                '$lte': datetime.datetime(self.st_year, self.st_month, self.st_day, 20, 0)}}},
                {'$group': {'_id': '$save_time', 'send_normal_gift_count': {'$sum': '$send_normal_gift_count'},
                            'send_normal_gift_amount': {'$sum': '$send_normal_gift_amount'},
                            }}
            ]
        )

        for x, y in zip(old_regist_gift_data, new_regist_gift_data):
            send_count[0][0], send_count[0][1] = x['send_normal_gift_count'], x['send_special_gift_count']
            send_count[1][0], send_count[1][1] = y['send_normal_gift_count'], y['send_special_gift_count']
        return send_count, send_amount

    # 画图表
    def chart_analysis_count(self):
        # 实例化图区
        fig = plt.figure(figsize=(12, 8), dpi=100)
        fig.suptitle('%s——统计图' %(str(time.strftime('%Y-%m-%d', time.localtime(int(time.mktime((self.end_year, self.end_month, self.end_day, 4, 0, 0, 0, 0, 0))))))),fontsize=16)
        # 在线人数
        name_list = ['登录人数', '参与游戏人数', '充值人数', '礼物消费人数', '完成过任务人数']
        old_users, new_users = self.get_dau_data()
        old_users_array, new_users_array = numpy.array(old_users), numpy.array(new_users)
        ax1 = fig.add_subplot(221)
        # 声明底部位置
        bottom=numpy.array([0,0,0,0,0])
        # 画老用户部分
        ax1.bar(numpy.arange(len(old_users)), old_users_array,width=0.3, bottom=bottom, tick_label=name_list, label='老用户',color='red')
        # 底部位置更新
        bottom+=old_users_array
        # 画新用户
        ax1.bar(numpy.arange(len(old_users)), new_users_array,width=0.3, bottom=bottom, label='新用户', color='blue')
        # 图例显示
        ax1.legend(loc="upper right", shadow=True)
        # 标题显示
        ax1.set_title('登录用户\n新：%s' % (str(new_users[0])))
        # 柱状图添加数值
        for x,y,z in zip(range(len(old_users)), old_users, new_users):
            ax1.text(x-0.1, y-12, y, color='white')
            ax1.text(x-0.1, y+1+z,z)

        # 读取充值数据
        pay_way_list = ['苹果支付','第三方支付']
        pay_data = self.get_pay_data()
        # 列出所有单价，排序
        price_list = []
        for each_price_log in pay_data:
            price_list.append(each_price_log['_id'])
        price_list.sort()
        # 列出单价对应的订单
        # for each_price_log in pay_data:


        # 读取csv获取游戏数据
        ext_count, ext_consume = self.get_ext_data()
        game_name = ['海盗船长\n', '智勇三张\n', '抓娃娃\n', '转转乐\n', '德州竞猜\n']
        for each_game in game_name:
            game_name[game_name.index(each_game)] = each_game + str(ext_consume[game_name.index(each_game)])
        # 3-画游戏图
        ax3 = fig.add_subplot(223)
        ax3.bar(numpy.arange(len(ext_count))+0.2, ext_count, width=0.2, tick_label=game_name)
        for x,y in zip(range(len(ext_count)), ext_count):
            ax3.text(x+0.05, y+1, y)
        ax33 = ax3.twinx()
        ax33.plot(numpy.arange(len(ext_count))+0.2, ext_consume, color='red')
        ax3.set_title('游戏流水 总计：%s  (豆子)' %str(sum(ext_consume)))
        ax3.set_ylabel('游戏次数(次)')

        # 获取礼物数据
        # gift_type = ['普通礼物', '特殊礼物']
        # gift_count, gift_amount = self.get_gift_data()
        # gift_amount_all = numpy.array(gift_amount[0]) + numpy.array(gift_amount[1])
        # ax4 = fig.add_subplot(224)
        # ax4.set_title('礼物统计 总计:%s  (豆子)' %str(sum(gift_amount_all)))
        # ax4.pie(gift_amount_all,labels=gift_type, autopct=make_autopct(gift_amount_all), colors=['cyan', 'violet'])
        # 保存、展示图表
        plt.savefig(self.data_file_save_path+'/user_chart.jpg')
        # plt.show()


    def daily_chart_users(self):
        data = pandas.read_csv(self.data_file_save_path + '/' + 'dau.csv')
        channels = self.get_all_channels(data)
        print(data[data['']])
        old_users, new_users, begin_card_use_count = self.get_dau_data()
        print(old_users, new_users)

    def get_all_channels(self, data):
        result_set = set()
        for channel in data.ix[:, 'channel']:
            result_set.add(channel)
        return list(result_set)
    # 保存csv
    def daily_csv_save(self):
        # 写入当天的all_users.csv文件
        # self.all_users()
        # 查询dau数据
        dau_users = self.user_filter()
        # 写入dau.csv
        dau_file_path = self.data_file_save_path + '/' + 'dau.csv'
        if os.path.exists(dau_file_path):
            pass
        else:
            at.write_csv(file_path=dau_file_path, head=all_users_keys, data=dau_users, keys=all_users_keys)

    # 保存每日数据
    def daily_data_insert(self):
        daily_data['date'] = self.save_timestamp
        if mongo.daily_data.find({'date':self.save_timestamp}).count() != 0:
            mongo.daily_data.remove({'date': self.save_timestamp})
        try:
            mongo.daily_data.insert(daily_data)
        except:
            daily_data['_id']= self.save_timestamp
            mongo.daily_data.insert(daily_data)
    # 用户留存分析
    def main(self, offset_day, channel=None):
        # 设置时间
        # 相隔的天数,默认为0
        self.offset_day = offset_day
        if channel:
            self.channel = channel
        else:
            self.channel = {'$regex':r'.*?'}
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

        print(self.save_date)
        # exit()
        self.save_timestamp = int(time.mktime((self.end_year, self.end_month, self.end_day, 0, 0, 0, 0, 0, 0)))
        self.start_timestamp = int(time.mktime((self.end_year, self.end_month, self.end_day, 4, 0, 0, 0, 0, 0)))
        self.finish_timestamp = int(time.mktime((self.end_year, self.end_month, self.end_day + 1, 4, 0, 0, 0, 0, 0)))


        self.data_file_save_path = 'D:/sparrow_data' + '/' + self.save_date
        if not os.path.exists(self.data_file_save_path):
            os.mkdir(self.data_file_save_path)
        print('将初始数据写入csv表保存')
        self.daily_csv_save()
        print('用初始数据作每日数据图')
        self.chart_analysis_count()
        # self.daily_chart_users()

class AnalysisTools:
    # 写入csv，
    # params：
    # file_path 保存路径/ head 首行 /keys data的键 /data 保存的数据
    def write_csv(self, file_path, head, keys, data):
        if os.path.exists(file_path):
            pass
        else:
            with open(file_path, 'w', newline='', encoding='utf-8') as fl:
                writer = csv.writer(fl, dialect='excel')
                writer.writerow(head)
                for each_data in data:
                    # 查询游戏消费
                    write_data = []
                    for each_key in keys:
                        try:
                            write_data.append(each_data[each_key])
                        except:
                            continue
                    writer.writerow(write_data)
            fl.close()

    def int64_to_int(self, data):
        new_data = []
        for each_data in data:
            new_data.append(int(each_data))
        return new_data

    def datetime_to_timestamp(self, time_str):
        return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    mongo = Mongo()
    aly = Analysis()
    at = AnalysisTools()
    for day in range(4, 5):
        start_time = time.clock()
        aly.main(day)
        print(time.clock()-start_time)
else:
    mongo = Mongo()
    aly = Analysis()
    at = AnalysisTools()