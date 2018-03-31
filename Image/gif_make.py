# 合成gif
from PIL import Image, ImageDraw, ImageFont
import os, imageio

source_path = 'C:\mediaSpider\Image/gif_source/'
font = ImageFont.truetype("/simhei.ttf",20)

def analysis_gif(pic_path, save_path):
    img = Image.open(pic_path)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    try:
        while True:
            current = img.tell()
            img.save(save_path + '/'+ str(current) + '.png')
            img.seek(current+1)
    except EOFError:
        pass

def img_draw(img_path, word):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 245), (500, 267)], fill=1)
    word_length = len(word)
    draw.text((250-int(word_length*10),247),word, fill=255, font=font)
    del draw
    img.save(img_path)

def add_word(words):
    pic_num = [range(8, 12), range(23, 32), range(38, 52), range(52, 71), range(71, 80), range(83, 90), range(96, 113), range(128, 138), range(138, 145)]
    for word, picture_nums in zip(words, pic_num):
        for picture_num in picture_nums:
            img_path = source_path + '%s.png'%str(picture_num)
            img_draw(img_path=img_path, word=str(word))

def make_gif():
    frames = []
    for image_name in range(0, 145):
        frames.append(imageio.imread('C:\mediaSpider\Image\gif_source/' + '%s.png'%str(image_name)))
    imageio.mimsave('C:\mediaSpider\Image/new.gif', frames, 'GIF', duration=0.1)

if __name__ == '__main__':
    words = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    add_word(words)
    make_gif()