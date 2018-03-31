import requests
import random, time, xlrd
from pymongo import MongoClient

# 期号与时间对应表
date_dict = {'0:35': '7', '22:45': '105', '11:10': '31', '10:50': '29', '1:25': '17', '21:50': '95', '21:40': '94', '21:20': '92', '23:10': '110', '21:30': '93', '23:35': '115', '23:00': '108', '22:50': '106', '22:40': '104', '23:30': '114', '10:00': '24', '1:10': '14', '10:40': '28', '19:10': '79', '14:30': '51', '23:05': '109', '0:20': '4', '19:40': '82', '0:05': '1', '0:15': '3', '11:50': '35', '0:10': '2', '11:20': '32', '14:40': '52', '1:15': '15', '23:40': '116', '23:45': '117', '20:00': '84', '20:10': '85', '18:30': '75', '18:50': '77', '22:10': '98', '13:40': '46', '0:50': '10', '19:30': '81', '13:10': '43', '17:30': '69', '21:00': '90', '12:30': '39', '17:50': '71', '18:40': '76', '15:10': '55', '1:00': '12', '15:50': '59', '22:15': '99', '23:55': '119', '18:00': '72', '12:20': '38', '18:20': '74', '14:00': '48', '13:30': '45', '20:50': '89', '13:20': '44', '1:50': '22', '0:30': '6', '23:25': '113', '1:40': '20', '0:40': '8', '1:30': '18', '19:50': '83', '11:40': '34', '16:10': '61', '0:55': '11', '14:10': '49', '1:45': '21', '14:20': '50', '23:50': '118', '22:55': '107', '23:20': '112', '0:45': '9', '22:35': '103', '12:00': '36', '20:30': '87', '17:00': '66', '12:10': '37', '12:50': '41', '19:00': '78', '22:05': '97', '20:40': '88', '20:20': '86', '1:20': '16', '1:05': '13', '0:25': '5', '10:30': '27', '22:20': '100', '10:10': '25', '15:30': '57', '18:10': '73', '11:00': '30', '22:30': '102', '16:50': '65', '11:30': '33', '15:40': '58', '13:50': '47', '22:00': '96', '17:10': '67', '21:10': '91', '22:25': '101', '16:20': '62', '23:15': '111', '00:00': '120', '15:20': '56', '13:00': '42', '17:20': '68', '1:35': '19', '1:55': '23', '16:40': '64', '17:40': '70', '15:00': '54', '16:00': '60', '10:20': '26', '14:50': '53', '12:40': '40', '16:30': '63', '19:20': '80'}

sleep_time = 0

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.SSC
        self.collection = self.db.NumHistory

# 判断当前时间是否获取,是返回期号，否返回false
def time_analysis():
    global sleep_time
    timestamp = time.time()
    time_local = time.localtime(timestamp)

    time_hour = time.strftime("%H", time_local)
    time_minute = time.strftime('%M', time_local)
    if (10 <= int(time_hour) < 22) and int(time_minute)%10 == 0:
        sleep_time = 500 # 间隔10分钟开奖的等待8分钟

        return date_dict[time_hour+':'+str(time_minute)]
    elif (int(time_hour) >= 22 or int(time_hour) <= 2) and (int(time_minute)%10 == 4 or int(time_minute)%10 == 9):
        sleep_time = 210
        return date_dict[time_hour+':'+str(int(time_minute)+1)]
    else:return False


def date_deal(date):
    timestamp = time.time()
    time_local = time.localtime(timestamp)

    time_year = time.strftime("%Y", time_local)[2:]
    time_month = time.strftime('%m', time_local)
    time_day = time.strftime('%d', time_local)
    if len(date) == 2:
        return time_year + time_month + time_day + '0' + date
    else:
        return time_year + time_month + time_day + date

def get_html_rep():
    url = 'http://buy.cqcp.net/Game/GetNum.aspx'
    Referer = 'http://buy.cqcp.net/game/cqssc/'
    ua = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'

    params = {'iType':11, 'name':random.uniform(0, 1)}
    while True:
        try:
            result = requests.get(url, headers={'User-Agent':ua, 'Referer':Referer}, params=params).text
            if result.find("|"):
                return result
        except Exception as e:
            print(e)

def get_num(date):
    print('查询期数%s的号码' %date)
    num_dict = {}
    num_dict['date'] = date
    while True:
        result = get_html_rep()
        print(result)
        date_get = result.split('|')[0]
        num = result.split('|')[1]
        if date_get == date:
            num_dict['num'] = num
            return num_dict
        else:
            print('没有得到最新的号码')
            time.sleep(2)

def search_control():
    # 开始
    print('等待查询时间')
    while True:
        this_date = time_analysis()
        if this_date:
            break
    print('开始查询')
    # 到了查询的时候
    this_date = date_deal(this_date)
    num_dict = get_num(this_date)
    print(num_dict['num'])
    insert_num(num_dict)
    print('冷却时间%s' % str(sleep_time))

    time.sleep(sleep_time)

    search_control()

def insert_num(num_dict):
    if mg.collection.find({'num':num_dict['num']}).count() == 0:
        local_time = time.localtime(time.time())
        str_time = time.strftime('%Y/%m/%d  %H:%M', local_time)
        num_dict['get_time'] = str_time
        mg.collection.insert(num_dict)
mg = Mongo()
search_control()
