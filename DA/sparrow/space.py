import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy
import os, csv, re
import matplotlib.pyplot as plt
from sparrow.tools import get_datetime, get_timestamp, write_csv

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
        self.db2 = self.client.sparrow_analysis

    def get_pay_data(self):
        third_pay_dataframe = pandas.DataFrame(list(self.third_pay.find({'paid':True}, {'source':1, 'price':1, 'pay_date':1, '_id':0})))
        third_pay_dataframe.rename(columns={'source':'user_id'}, inplace=True)
        third_pay_dataframe['source'] = 'third'
        third_pay_dataframe['pay_date'] = third_pay_dataframe['pay_date'].apply(lambda x:str(x).split(' ')[0])
        third_pay_dataframe['price'] = third_pay_dataframe['price'].apply(lambda x: x/100)

        apple_pay_dataframe = pandas.DataFrame(list(self.apple_pay.find({}, {'source': 1, 'price': 1, 'date': 1, '_id':0})))
        apple_pay_dataframe.rename(columns={'source': 'user_id', 'date': 'pay_date'}, inplace=True)
        apple_pay_dataframe['source'] = 'apple'
        apple_pay_dataframe['pay_date'] = apple_pay_dataframe['pay_date'].apply(lambda x: str(x).split(' ')[0])
        apple_pay_dataframe['price'] = apple_pay_dataframe['price'].apply(lambda x: x/100)

        users_pay_dataframe = pandas.concat([third_pay_dataframe, apple_pay_dataframe], ignore_index=True)
        users_pay_dataframe.to_csv('ppp.csv',encoding='utf-8')
if __name__ == '__main__':
    mon = Mongo()
    mon.get_pay_data()