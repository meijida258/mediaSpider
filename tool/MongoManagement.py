from pymongo import MongoClient
''' mongodb命令符
    $gt -------- greater than
    $gte --------- gt equal
    $lt -------- less than
    $lte --------- lt equal
    $ne ----------- not equal
'''
class MongoSet:
    # insert_dict args 1.要保存的数据 2.要保存的数据库集合名 3.用来验证的key
    def insert_dict(self, need_insert_data,database_collection,  verify_key=None):
        if type(need_insert_data) == list:
            for each_data in need_insert_data:
                self.insert_dict_(each_data, database_collection, verify_key)
            return
        elif type(need_insert_data) == dict:
            self.insert_dict_(need_insert_data, database_collection, verify_key)
            return

    def insert_dict_(self, need_insert_dict,database_collection,  verify_key=None):
        if verify_key:
            if database_collection.find({verify_key:need_insert_dict[verify_key]}).count() == 0:
                database_collection.insert(need_insert_dict)
                print ('%s插入一条信息' % str(database_collection))
            else:
                print ('该条信息已存在')
        else:
            database_collection.insert(need_insert_dict)

    def remove_dict(self, verify_dict, database_collection):
        message_count = database_collection.find(verify_dict).count()
        database_collection.remove(verify_dict)
        print ('%s移除掉%s条包含%s的信息' % (str(database_collection), str(message_count), str(verify_dict)))



if __name__ == '__main__':
    mon = MongoSet()
    client = MongoClient('localhost', 27017)
    db = client.TestDb
    collection = db.TestDicts
    collection.insert({'code':1, 'name':['leo', 'lee']})
    b = list(collection.find({'code':1}))
    print(b)
    print(b[0]['name'])
    # mon.remove_dict('a', 1000, collection)
else:
    mon = MongoSet()
