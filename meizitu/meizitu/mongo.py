from pymongo import MongoClient

class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.MeiTu
        self.collection = self.db.pic

    def insert(self, identify_key, need_save_dict, save_collection=None):
        if not save_collection:
            save_collection = self.collection
        if save_collection.find({identify_key:need_save_dict[identify_key]}).count() == 0:
            save_collection.insert(need_save_dict)
            print('保存%s的第%s张图片' % (need_save_dict['pic_title'], (need_save_dict['pic_url'].split('/')[-1]).split('.')[0]))
        else:
            print('%s的第%s张图片已存在')