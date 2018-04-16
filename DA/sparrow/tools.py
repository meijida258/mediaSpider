#-------------------------------------------------------------------------
#   程序：tools
#   日期：2018.2.12
#   功能：常用的转换函数
#-------------------------------------------------------------------------
import time, os, csv

# 根据时间戳和偏移天数得到datetime
def get_datetime(timestamp, off_day):
    year, month, day, hour = int(time.strftime('%Y', time.localtime(timestamp - 86400 * off_day))), int(
        time.strftime('%m', time.localtime(timestamp - 86400 * off_day))), int(
        time.strftime('%d', time.localtime(timestamp - 86400 * off_day))), int(
        time.strftime('%H', time.localtime(timestamp - 86400 * off_day)))
    return year, month, day, hour

# 写入csv，
# params：
# file_path 保存路径/ head 首行 /keys data的键 /data 保存的数据
def write_csv(file_path, head, keys, data):
    if os.path.exists(file_path):
        os.remove(file_path)
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

def int64_to_int(data):
    new_data = []
    for each_data in data:
        new_data.append(int(each_data))
    return new_data

def datetime_to_timestamp(time_str):
    return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))

def get_timestamp(year, month, day, hour):
    dt = "{}-{}-{} {}:0:0".format(year, month, day, hour)
    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    return timestamp