# -*- coding: UTf-8 -*-
from pymongo import MongoClient

class Mongo:
    def insert_dict(self, need_insert_dict, verify_key, database_collection):
        if database_collection.find({verify_key:need_insert_dict[verify_key]}).count() == 0:
            database_collection.insert(need_insert_dict)
            print ('%s插入一条信息' % str(database_collection))
            return True
        else:
            print ('该条信息已存在')
            return False
    def remove_dict(self, verify_key, verify_key_value, database_collection):
        message_count = database_collection.find({verify_key:verify_key_value}).count()
        database_collection.remove({verify_key:verify_key_value})
        print ('%s移除掉%s条键为%s键值为%s的信息' % (str(database_collection), str(message_count), str(verify_key), str(verify_key_value)))

    def update_dict(self, verify_key, verify_key_value, update_key,new_key_value, database_collection):
        message_count = database_collection.find({verify_key:verify_key_value}).count()
        if message_count > 0:
            database_collection.update({verify_key:verify_key_value}, {'$set':{update_key:new_key_value}})
            print ('%s将%s条消息修改为新键值%s' % (str(database_collection), str(message_count), str(new_key_value)))

if __name__ == '__main__':
    mon = Mongo()
    client = MongoClient('localhost', 27017)
    db = client.TestDb
    collection = db.TestDicts
    a = collection.find().count()
    print (collection.find()[0])
    # mon.remove_dict('a', 1000, collection)
else:
    mon = Mongo()
