import os, sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import statsmodels.formula.api as sfa
import pandas as pd
import numpy as np
from pymongo import MongoClient
from users_lottery import UserLotteryLog
from gift_lottery import GiftLotteryLog
import datetime
from sklearn import linear_model

class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.sparrow_main
        self.all_users = self.db.users
        self.users_login_log = self.db.login_log
        self.apple_pay = self.db.apple_iap_log
        self.daily_data = self.db.daily_deal_data
        self.third_pay = self.db.recharge_orders
        self.daily_task_log = self.db.daily_task_log
        self.db2 = self.client.sparrow_analysis

        self.gift_log = self.db.gift_log
        self.gift_lottery_log = self.db.gift_lottery_log

class SMF_Pre:
    def __init__(self):
        pass
    def con1(self):
        p_data = ull.get_users_pay_data(start_date=datetime.datetime(*[2018,11,1,0,0]),
                               end_date=datetime.datetime(*[2018,12,1,0,0]))
        p_data_by_date = pd.pivot_table(p_data, values=['price'],index=['date'],aggfunc=np.sum).reset_index()
        l_data = mgs.gift_log.find({'date':{'$gte':datetime.datetime(*[2018,11,1,0,0]),
                                            '$lte':datetime.datetime(*[2018,12,1,0,0])}},
                                    {'_id':0, 'gift.price':1, 'date':1})
        l_data = pd.DataFrame(list(l_data))
        l_data['gift'] = l_data['gift'].apply(lambda x:x['price'])
        l_data['date'] = l_data['date'].apply(lambda x:str(x).split()[0])
        l_data_by_date = pd.pivot_table(l_data, values=['gift'], index=['date'],aggfunc=np.sum).reset_index()
        join_data = p_data_by_date.join(l_data_by_date['gift'])
        join_data.to_csv('con1.csv')

    def smf(self,data, formula):
        fit_result = sfa.ols(data=data, formula=formula).fit()
        print(fit_result.summary())

    def skl_lm(self):
        data = pd.read_csv('con1.csv')
        reg = linear_model.LinearRegression()
        reg.fit(data.price, data.gift)
        print(reg.coef_)

    def lottery_log(self):
        start_date = datetime.datetime(*[2018,4,1,0,0])
        end_date = datetime.datetime(*[2018,12,30,0,0])
        task_log = ull.task_reward_data(start_date, end_date)
        task_sum = np.sum(pd.DataFrame(list(task_log)).reward)
        print(task_sum)
        # 签到
        sign_in_log = ull.sign_in_log_data(start_date,end_date)
        sign_in_sum = np.sum(pd.DataFrame(list(sign_in_log)).reward)
        print(sign_in_sum)
        # 抽奖
        lottery_log = ull.get_users_lottery_data(start_date, end_date)
        lottery_log_df = pd.DataFrame(list(lottery_log))
        lottery_log_df['award'] = lottery_log_df['lottery_award'].apply(lambda x:x['reward'])
        lottery_sum = np.sum(lottery_log_df.award)
        print(lottery_sum)
        # 在线
        online_log = ull.users_online_reward_data(start_date,end_date)
        online_sum = np.sum(pd.DataFrame(list(online_log)).reward)
        print(online_sum)
        m = task_sum+sign_in_sum+lottery_sum+online_sum
        print(m/100)
if __name__ == '__main__':
    mgs = MongoSet()
    sp = SMF_Pre()
    ull = UserLotteryLog()
    gll = GiftLotteryLog()
    # sp.con1()
    sp.lottery_log()