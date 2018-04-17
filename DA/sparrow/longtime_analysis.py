# 分析7天的数据
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy
import os, csv
import matplotlib.pyplot as plt
from sparrow.sparrow_main import Analysis as AnalysisMain
from sparrow.daily_analysis import AnalysisTools

source_data_path = 'D:/sparrow_data/'
file_save_path = 'D:/sparrow_data/main_analysis/'

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.sparrow_main
        self.all_users = self.db.users
        self.users_login_log = self.db.login_log
        self.beginner_card_log = self.db.beginner_card_log
        self.db2 = self.client.sparrow_analysis
        self.daily_data = self.db2.daily_deal_data


class Analysis:
    # 分析一段时间的用户留存
    def user_store_analysis_main(self):
        # 获取时间段内的用户情况
        today_timestamp = time.time()
        result, result_proportion = [], []
        for day in range(58, 27, -1):
            end_date= self.get_datetime(today_timestamp, day)
            start_date= self.get_datetime(today_timestamp, day+1)
            # 获取当天注册的用户
            new_users = mon.all_users.find({'regist_date':{'$gte': datetime.datetime(start_date[0], start_date[1], start_date[2], 20, 0),
                     '$lte': datetime.datetime(end_date[0], end_date[1], end_date[2], 20, 0)},
                                            'username': {'$regex': r'^(?!robot_[0-9]{5})'}})
            # 通过获取的用户进行留存分析
            user_store_result = self.user_store_analysis(new_users, end_date=end_date, start_date=start_date)
            user_store_result.insert(0, datetime.datetime(start_date[0], start_date[1], start_date[2], 20, 0))
            result.append(user_store_result)
            # 计算留存率
            user_store_proportion = user_store_result[:]
            for each_result_index in range(1, len(user_store_result)):
                if type(user_store_result[each_result_index]) == int:
                    user_store_proportion[each_result_index] = user_store_result[each_result_index] / user_store_result[1]
                else:
                    user_store_proportion[each_result_index] = ''
            result_proportion.append(user_store_proportion)
        # 输出csv文件
        head = ['日期','新用户','次日','3天','7天','14天','30天','60天']
        path = file_save_path + '1月留存率.csv'
        self.write_csv(file_path=path, head=head, data=result, keys=head)

    # 画分析图
    def chart_user_store(self, month):
        # 1.获取留存数据
        data = pandas.read_csv(file_save_path + '%s月留存率.csv' % str(month))
        # 原始数据
        user_store = []
        for row in range(0, data.shape[0]):
            user_store.append(data.ix[row, :])
        # 将每个数据集分为4部分
        cut_deal_data = self.get_cut_deal_data(user_store, cut_time=4)

        fig = plt.figure(figsize=(12, 6), dpi=100)
        fig.suptitle('%s月' %str(month))
        # 1.画当期数据集的留存图

        ax1 = fig.add_subplot(211)
        colors = ['r','g','blue','black']
        labels = ['第一周','第二周','第三周','第四周']
        x_ticks = [0,1,3,7,14,30]
        deal_data_proportion_all = numpy.array([0]*6).astype(numpy.float64)
        for deal_data in cut_deal_data:
            deal_data_proportion = []
            for each_data in deal_data[:-1]:
                deal_data_proportion.append(each_data/deal_data[0])
            ax1.plot([0,1,3,7,14,30], deal_data_proportion, color=colors[cut_deal_data.index(deal_data)], label=labels[cut_deal_data.index(deal_data)])

            deal_data_proportion_all += numpy.array(deal_data_proportion)
        for i in range(1, len(deal_data_proportion_all)):
            if deal_data_proportion_all[i] > 0:
                ax1.text(x_ticks[i], deal_data_proportion_all[i]/4, '%.2f%%' % (deal_data_proportion_all[i]/4*100))
        ax1.set_ylim(0, 1.1)
        ax1.set_xticks(x_ticks)
        ax1.set_yticklabels([0, '20%','40%','60%','80%','100%'])
        ax1.set_title('周留存')
        plt.legend()

        # 2.画每日用户情况
        # 2-1 新用户,老用户
        login_log_date, login_new_users, login_all_users = [], [], []
        for i in user_store:
            show_date = str(i['日期']).split(' ')[0].split('-')[-1]
            login_log_date.append(show_date)
            login_new_users.append(i['新用户'])
            login_all_users.append(self.get_old_users_count([int(str(i['日期']).split(' ')[0].split('-')[0]),
                                                             int(str(i['日期']).split(' ')[0].split('-')[1]),
                                                             int(str(i['日期']).split(' ')[0].split('-')[2])]))
        login_new_users_array = numpy.array(login_new_users)
        login_old_users_array = numpy.array(login_all_users) - login_new_users_array
        # 声明底部位置
        bottom = numpy.array([0]*len(login_new_users))
        # 画第一部分柱状图
        ax2 = fig.add_subplot(212)
        # 先画老用户
        ax2.bar(numpy.arange(len(login_new_users)), login_old_users_array, width=0.2, bottom=bottom,tick_label=login_log_date, color='deeppink', label='老用户')
        # 更新底部位置，在画新用户
        bottom +=login_old_users_array
        ax2.bar(numpy.arange(len(login_new_users)), login_new_users_array, width=0.2, bottom=bottom, color='peru', label='新用户')
        # 平均日活
        ax2.plot(numpy.arange(len(login_new_users)), [sum(login_all_users)/len(login_new_users)]*len(login_new_users), '--', color='pink')
        ax2.text(len(login_new_users)+1, sum(login_all_users)/len(login_new_users), '平均活跃人数\n%s' %str(int(sum(login_all_users)/len(login_new_users))))
        # 平均新用户
        ax2.plot(numpy.arange(len(login_new_users)),
                 [sum(login_new_users_array) / len(login_new_users)] * len(login_new_users), '--', color='blueviolet')
        ax2.text(len(login_new_users) + 1, sum(login_new_users_array) / len(login_new_users),
                 '平均新用户\n%s' % str(int(sum(login_new_users_array) / len(login_new_users))))
        # 平均老用户
        ax2.plot(numpy.arange(len(login_new_users)),
                 [sum(login_old_users_array) / len(login_new_users)] * len(login_new_users), '--', color='coral')
        ax2.text(len(login_new_users) + 1, sum(login_old_users_array) / len(login_new_users),
                 '平均老用户\n%s' % str(int(sum(login_old_users_array) / len(login_new_users))))
        ax2.set_title('用户情况')
        plt.legend()
        plt.savefig(file_save_path + '%s月.jpg' %str(month))
        plt.show()

    # 获取老用户的数量
    def get_old_users_count(self, data_date):
        dic_name = str(datetime.datetime(data_date[0], data_date[1], data_date[2], 0, 0)).split(' ')[0]
        data_path = source_data_path + dic_name + '/dau.csv'
        data = pandas.read_csv(data_path)
        return data.shape[0]

    def get_cut_deal_data(self, source_data, cut_time):
        # 将每个数据集分为n部分
        cut_num = int(len(source_data) / cut_time)
        cut_deal_data = []
        column_label = ['日期','新用户','次日','3天','7天','14天','30天','60天']
        for i in range(0, cut_time):
            week_user_store = [0] * 7
            if i == 0:
                user_store_data = source_data[0:(i + 1) * cut_num]
            elif i == 3:
                user_store_data = source_data[i * cut_num + 1:]
            else:
                user_store_data = source_data[i * cut_num + 1:(i + 1) * cut_num]
            for each_data in user_store_data:
                week_user_store[0] += each_data['新用户']
                week_user_store[1] += each_data['次日']
                week_user_store[2] += each_data['3天']
                week_user_store[3] += each_data['7天']
                week_user_store[4] += each_data['14天']
                week_user_store[5] += each_data['30天']
                week_user_store[6] += each_data['60天']
            cut_deal_data.append(week_user_store)
        return cut_deal_data

    # 某个用户集合的留存分析
    # 主要分析次日 3天 7天 14天 30天的情况，以用户id作为依据
    def user_store_analysis(self, users, start_date, end_date):
        # 开始计算的时间搓
        start_timestamp = self.get_timestamp(year=start_date[0], month=start_date[1], day=start_date[2], hour=20)
        # 得到某天的新增用户
        user_store_log = [0] * 7
        user_store_log[0] = users.count()
        for each_user in users:
            need_query_days = [1, 3, 7, 14, 30, 60]
            for query_day in need_query_days:
                user_store_query_result = self.user_store_query(str(each_user['_id']), start_timestamp=start_timestamp, query_days=query_day)
                if user_store_log[need_query_days.index(query_day) + 1] == '':
                    break
                if user_store_query_result == 'timeout':
                    user_store_log[need_query_days.index(query_day) + 1] = ''
                elif user_store_query_result == 'yes':
                    user_store_log[need_query_days.index(query_day) + 1] += 1
        return user_store_log

    # 计算某段时间内某个用户的留存情况, 暂以login_log作为依据
    def user_store_query(self, user_id, start_timestamp, query_days):
        query_start_date = self.get_datetime(timestamp=start_timestamp, off_day=-query_days)
        query_end_date = self.get_datetime(timestamp=start_timestamp, off_day=-(1+query_days))

        if start_timestamp + (1+query_days)*86400 - time.time() > 0:
            return 'timeout'
        user_store_result = mon.users_login_log.find({'source':user_id, 'date':{'$gte':datetime.datetime(query_start_date[0], query_start_date[1], query_start_date[2], 20, 0),
                                                                                  '$lte':datetime.datetime(query_end_date[0], query_end_date[1], query_end_date[2], 20, 0)}}).count()
        if user_store_result > 0:
            return 'yes'
        else:
            return 'no'

    # 计算用户相关数据，以月为单位
    def get_user_deal_data(self, year, month):
        days = []
        off_day = 0
        start_timestamp = self.get_timestamp(year, month, 1, 0)
        while True:
            if self.get_datetime(start_timestamp, off_day=-off_day)[1] != month:
                break
            else:
                days.append(self.get_datetime(start_timestamp, off_day=-off_day)[2])
            off_day += 1
        deal_data = []
        for everyday in days:
            today_data = {}
            today_data['date'] = str(datetime.datetime(year, month, everyday)).split(' ')[0]
            data_file_path = source_data_path + today_data['date'] + '/dau.csv'
            try:
                data = pandas.read_csv(data_file_path)
            except:
                break
            # 登录用户
            today_data['login_user_count'] = data.shape[0]
            # 新用户
            today_data['regist_user_count'] = 0
            # 充值用户数，充值金额
            today_data['pay_user_count'], today_data['pay_amount'] = 0, 0
            # 游戏用户
            today_data['game_user_count'] = 0
            # 登录奖励人数
            today_data['sign_in_reward_user_count'] = 0
            # 在线奖励人数
            today_data['online_reward_user_count'] = 0
            # 任务人数
            today_data['task_reward_user_count'] = 0

            for row in range(0, data.shape[0]):
                # 新用户注册
                if data.ix[row, 'regist_date'].split(' ')[0] == today_data['date']:
                    today_data['regist_user_count'] += 1
                # 充值用户数， 充值总额
                if data.ix[row, 'coin_trader_count'] > 0 or data.ix[row, 'apple_pay_count'] > 0 or data.ix[row, 'third_pay_count'] > 0:
                    today_data['pay_user_count'] += 1
                    today_data['pay_amount'] = today_data['pay_amount'] + (data.ix[row, 'coin_trader_amount'] + data.ix[row, 'apple_pay_amount'] + data.ix[row, 'third_pay_amount'])/100

                # 定义一个判断大于0 的lambda
                my_lambda = lambda x: 1 if x > 0 else 0
                # 游戏用户数
                today_data['game_user_count'] += my_lambda(data.ix[row, 'ext_count'])
                # 登录奖励人数
                today_data['sign_in_reward_user_count'] += my_lambda(data.ix[row, 'sign_in_reward'])
                # 在线奖励人数
                today_data['online_reward_user_count'] += my_lambda(data.ix[row, 'online_reward'])
                # 任务人数
                today_data['task_reward_user_count'] += my_lambda(data.ix[row, 'task_count'])
            deal_data.append(today_data)
        return deal_data

    def user_data_analysis(self):
        year, month = 2018, 2
        deal_data = self.get_user_deal_data(year=year, month=month)
        csv_head = ['日期', '登录用户', '新用户注册', '游戏用户', '登录奖励人数', '在线奖励人数', '任务人数', '充值用户数', '充值总额']
        csv_keys = [ 'date', 'login_user_count', 'regist_user_count', 'game_user_count', 'sign_in_reward_user_count', 'online_reward_user_count', 'task_reward_user_count', 'pay_user_count', 'pay_amount']
        self.write_csv(file_save_path + '%s月数据.csv' %str(month), head=csv_head, keys=csv_keys, data=deal_data)

    # 计算新用户的行为
    # def user_new_regist_behaviors(self):
    def get_datetime(self, timestamp, off_day):
        year, month, day, hour = int(time.strftime('%Y', time.localtime(timestamp - 86400 * off_day))), int(
            time.strftime('%m', time.localtime(timestamp - 86400 * off_day))), int(
            time.strftime('%d', time.localtime(timestamp - 86400 * off_day))),int(time.strftime('%H', time.localtime(timestamp - 86400 * off_day)))
        return year, month, day, hour

    def get_timestamp(self, year, month, day, hour):
        return int(time.mktime((int(year), int(month), int(day), int(hour), 0, 0, 0, 0, 0)))

    def get_date_to_str(self, date):
        time_str = str(date)
        return time_str.split(' ')[0]

    def write_csv(self, file_path, head, keys, data):
        with open(file_path, 'w', newline='', encoding='utf-8') as fl:
            writer = csv.writer(fl, dialect='excel')
            writer.writerow(head)
            for each_data in data:
                if type(each_data) == list:
                    writer.writerow(each_data)
                else:
                    write_data = []
                    for each_key in keys:
                        write_data.append(each_data[each_key])
                    writer.writerow(write_data)
        fl.close()


if __name__ == '__main__':
    mon = Mongo()
    aly = Analysis()
    analysis_main = AnalysisMain()
    analysis_tool = AnalysisTools()
    st = time.time()
    # aly.user_store_analysis_main()
    # aly.chart_user_store(month=1)
    aly.user_data_analysis()
    print(time.time()-st)