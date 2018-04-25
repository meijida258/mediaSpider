#-------------------------------------------------------------------------
#   程序：users_behavior
#   日期：2018.4.12
#   功能：获取消费行为的数据
#-------------------------------------------------------------------------
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy
import matplotlib.pyplot as plt

source_data_path = 'D:/sparrow_data/'
file_save_path = 'D:/sparrow_data/main_analysis/'


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
        self.db = self.client.sparrow_main
        self.all_users = self.db.users
        self.users_login_log = self.db.login_log
        self.apple_pay_log = self.db.apple_iap_log
        self.android_pay_log = self.db.recharge_orders
        self.daily_task_log = self.db.daily_task_log
        self.lottery_log = self.db.lottery_log
        self.db2 = self.client.sparrow_analysis

class UserPayAnalysis:
    def __init__(self):
        pass

    @time_clock
    def get_pay_log_apple(self, start_date, end_date)-> pandas.DataFrame():
        # 查询时间段内的数据，只返回用户id，价格，时间
        apple_pay_log = mongo.apple_pay_log.find({'date':{'$gte':datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                                          '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}},
                                                 {'_id':0, 'source':1, 'price':1, 'date':1})
        apple_pay_df = pandas.DataFrame(list(apple_pay_log))
        return apple_pay_df
    def get_pay_log_android(self, start_date, end_date):
        android_pay_log = mongo.android_pay_log.find({'paid':True,'pay_date':{'$gte':datetime.datetime(start_date[0], start_date[1], start_date[2], 0, 0),
                                                          '$lte':datetime.datetime(end_date[0], end_date[1], end_date[2], 0, 0)}},
                                                 {'_id':0, 'source':1, 'price':1, 'pay_date':1})
        android_pay_df = pandas.DataFrame(list(android_pay_log))
        return android_pay_df

    @time_clock
    def get_user_pay_sum(self, data):
        # 根据user_id返回求和的数据
        pay_sum = data['price'].groupby(data['user_id']).sum()
        pay_sum_df = pay_sum.to_frame()
        pay_sum_df['user_id'] = pay_sum_df.index
        pay_sum_df.rename(columns={'price': 'pay_price'}, inplace=True)
        return pay_sum_df
    # def user_pay_analysis(self):
    #     csv_head = ['user_id', 'user_regist_date', '当日付费', '3天付费', '7天付费', '14天付费']
    #     data = pandas.read_csv(file_save_path + '{}.csv'.format(self.csv_name))
    #     fig = plt.figure()
    #     ax1 = fig.add_subplot(211)
    #     pay_user_count, pay_amount = [0]*4, [0]*4
    #     for row in range(0, data.shape[0]):
    #         for head in csv_head[2:]:
    #             if int(re.findall(r'\[\[(.*)\], \[(.*)\]\]', data.ix[row, head])[0][0]) > 0:
    #                 pay_user_count[csv_head.index(head)-2] += 1
    #                 pay_amount[csv_head.index(head)-2] += round(float(re.findall(r'\[\[(.*)\], \[(.*)\]\]', data.ix[row, head])[0][1]))
    #     pay_proportion = numpy.array(pay_user_count) / data.shape[0]
    #     pay_average = numpy.array(pay_amount) / numpy.array(pay_user_count) / 100
    #     ax1.bar(numpy.arange(len(pay_proportion)), pay_proportion, tick_label=csv_head[2:], width=0.2, color='blueviolet')
    #     ax1.set_ylabel('付费率')
    #     ax11 = ax1.twinx()
    #     ax11.plot(numpy.arange(len(pay_proportion)), pay_average, color='plum')
    #     ax11.set_ylabel('平均付费金额')
    #     for i in range(0, len(pay_proportion)):
    #         try:
    #             ax11.text(i, pay_average[i], int(pay_average[i]))
    #         except:
    #             ax11.text(i, pay_average[i], 0)
    #         ax1.text(i-0.05 ,pay_proportion[i]+0.001, '%.2f%%' %(pay_proportion[i]*100))
    #     pic_path = file_save_path+'{}.jpg'.format(self.pic_name)
    #
    #     plt.savefig(pic_path)
    #     plt.show()

    def get_datetime_list(self, iso_datetime):
        return [iso_datetime.year, iso_datetime.month, iso_datetime.day, iso_datetime.hour]

    def users_pay_main(self, start_date, end_date):
        pay_df_apple = up.get_pay_log_apple(start_date, end_date)  # 获得数据
        pay_df_apple['how'] = 'apple'  # 添加列
        pay_df_android = up.get_pay_log_android(start_date, end_date)  # 获得数据
        pay_df_android.rename(columns={'pay_date': 'date'}, inplace=True)  # 修改列名
        pay_df_android['how'] = 'android'  # 添加列
        users_pay_df = pandas.concat([pay_df_apple, pay_df_android])  # 合并数据
        users_pay_df['date'] = users_pay_df['date'].apply(lambda x: str(x).split(' ')[0])  # 日期格式修改为%y-%m-%d
        users_pay_df.rename(columns={'source': 'user_id'}, inplace=True)
        # users_pay_df.to_csv('pay.csv', index=False)
        return users_pay_df

    def chart_pay_img(self, users_pay_df):
        df = pandas.pivot_table(users_pay_df, values='price', index=['how'], columns=['date'],
                                aggfunc=numpy.sum).fillna(0)
        figure = plt.figure(figsize=(12, 8), dpi=100)
        ax = figure.add_subplot(111)
        lable_list = df.columns
        android_array, apple_array = df.ix['android'].values, df.ix['apple'].values
        bottom=numpy.array([0.0]*len(android_array))
        # 画老用户部分
        ax.bar(numpy.arange(len(android_array)), android_array,width=0.3, bottom=bottom, tick_label=lable_list, label='android',color='red')
        # 底部位置更新
        bottom+=android_array
        # 画新用户
        ax.bar(numpy.arange(len(android_array)), apple_array,width=0.3, bottom=bottom, label='apple', color='blue')
        # 图例显示
        ax.legend(loc="upper right", shadow=True)
        plt.show()

if __name__ == '__main__':
    mongo = Mongo()
    up = UserPayAnalysis()
    start_date, end_date = [2018, 4, 1, 0, 0], [2018, 4, 20, 0, 0]
    user_pay_df = up.users_pay_main(start_date=start_date, end_date=end_date)
    up.chart_pay_img(users_pay_df=user_pay_df)
else:
    mongo = Mongo()