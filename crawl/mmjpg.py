import asyncio, time, re, os, requests, json, random, datetime
from lxml import etree
from multiprocessing.dummy import Pool
from pymongo import MongoClient
from PIL import Image
from tool.ImgOut import iop

client = MongoClient('localhost', 27017)
db = client.MMjpg
collection1 = db.Image1
collection2 = db.Image2
collection3 = db.Image3
collection4 = db.Image4
set_path = 'C:/Users/Administrator/Desktop/图/fhx20161004'
out_path = 'C:/Users/Administrator/Desktop'

def random_output(output_path, source_collection):
    st = time.time()
    img_list = source_collection.find()
    img_random = img_list[random.randint(0, img_list.count())]
    img_set_name = img_random['set_name']
    img_set_list = source_collection.find({'set_name':img_set_name})
    if not os.path.exists(output_path + os.path.sep + img_set_name):
        os.mkdir(output_path + os.path.sep + img_set_name)
    for img_dict in img_set_list:
        save_path = output_path + os.path.sep + img_dict['set_name'] + os.path.sep + img_dict['img_num'] + '.' + img_dict['img_type']
        with open(save_path, 'wb') as img:
            img.write(img_dict['img_data'])
        img.close()
    print('输出完毕，耗时%s' % str(time.time()-st))
# iop.random_output(out_path, collection4)
def insert_pic(i, save_collection = collection4):
    img_name_list = os.listdir(set_path + os.path.sep + i)
    for each_img in img_name_list:
        if save_collection.find({'set_name': i, 'img_num': each_img.split('.')[0]}).count() == 0:
            start_time = time.time()
            with open(set_path + os.path.sep + i + os.path.sep + each_img, 'rb') as img:
                img_data = img.read()
            img.close()
            insert_dict = {}
            insert_dict['img_data'] = img_data
            insert_dict['set_name'] = i
            insert_dict['img_type'] = each_img.split('.')[-1]
            insert_dict['img_num'] = each_img.split('.')[0]
            save_collection.insert(insert_dict)
            print('录入一张图片，来自%s的第%s张图片，耗时%s' % (insert_dict['set_name'], insert_dict['img_num'], str(time.time() - start_time)))

exit()
b = requests.get('http://imgs.aixifan.com/live/1493028073796/1493028073796.jpg').content

fl = open('a.txt', 'wb')
fl.write(b)
fl.close()
fl = open('a.txt', 'rb')
with open('b.jpg', 'wb') as c:
    c.write(fl.read())
c.close()