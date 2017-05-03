import os, time, random
class ImgOutPut:
    def random_output(self, output_path, source_collection):
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

if __name__ == '__main__':
    iop = ImgOutPut()
else:
    iop = ImgOutPut()