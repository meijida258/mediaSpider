# -*- coding: UTF-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

class Img:
    def __init__(self):
        self.imgs_path = os.getcwd()


    def get_all_img(self):
        img_paths = os.listdir(self.imgs_path)
        for img_path in img_paths:
            if img_path.endswith('jpg') or img_path.endswith('png'):
                self.resize_img(img_path)

    def resize_img(self, img_path):
        img_all_path = os.getcwd() + os.path.sep + img_path
        img_value = Image.open(img_all_path)
        width, height = img_value.size
        if width / 1920 >= 1 or height / 1920 >=1 :
            resize_times = max(float(width)/1920, float(height)/1920)
            img_value.resize((int(width/resize_times), int(height/resize_times)),Image.ANTIALIAS).save(img_all_path,quality=95)

class AddWord:
    def addWord(self):
        img0 = Image.open('C:/Users/Administrator/Desktop/stage2.jpg').convert('RGBA')
        draw = ImageDraw.Draw(img0)
        mp = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 40)
        #draw.text((130,350), u'鬼镇',font=mp, fill='white')
        draw.text((50,350), u'崇光精神病院',font=mp, fill='white')
        mp = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 30)
        draw.text((10,430), u'难度：',font=mp, fill='yellow')
        draw.text((100,430), u'★ ★ ★ ★',font=mp, fill='red')
        #alpha = Image.open('D:/endless_zombies/Assets/Main/Art/UI/claw.png')
        #img0.paste(alpha, (30,430))
        img0.save('C:/Users/Administrator/Desktop/stage2_deal.png')
if __name__ == '__main__':
    #addw = AddWord()
    #addw.addWord()
    for a in range(10, -10):
        print (a)
    #print('\n'.join([''.join([('Love'[(x-y) % len('Love')] if ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3 <= 0 else ' ') for x in range(-30, 30)]) for y in range(30, -30, -1)]))

