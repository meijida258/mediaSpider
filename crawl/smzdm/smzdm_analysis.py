from tool.GetHtml import hp
from pymongo import MongoClient
import time, xlwt
class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.SMZDM
        self.goods_collection = self.db.Goods

class DateGet:
    def get_someday_data(self, start_time, end_time=None):
        if not end_time:
            end_time = int(time.time() * 100)
        goods_data = mon.goods_collection.find({'$and':[{'time_sort':{'$lt':end_time}}, {'time_sort':{'$gt':start_time}}]})
        return goods_data

    def get_regex_data(self, key, regex_value):
        # goods_data = mon.goods_collection.find({key:{'$regex': regex_value}})
        goods_data = mon.goods_collection.find({'$and':[{key: {'$regex': regex_value}}, {'time_sort':{'$gt':((int(time.time()) - 86400 * 3)*100)}}]})
        return goods_data


    def make_excel(self, goods_data):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('goods_data')
        row, column = 1, 1
        for each_good in goods_data:
            try:
                worksheet.write(column, row, each_good['goods_name'])
                worksheet.write(column, row + 1, each_good['goods_from'])
                worksheet.write(column, row + 2, each_good['goods_url'])
                worksheet.write(column, row + 3, each_good['goods_date'])
                worksheet.write(column, row + 4, each_good['goods_price'])
                worksheet.write(column, row + 5, each_good['goods_category'])
            except:
                break
            column += 1
        workbook.save('hahaha.xls')

    def main(self):
        # end_time = int(time.time()*100)
        # goods_data = self.get_someday_data(end_time - 8640000, end_time)
        goods_data = self.get_regex_data('goods_name', '耳机')
        self.make_excel(goods_data)

if __name__ == '__main__':
    mon = Mongo()
    dg = DateGet()
    dg.main()