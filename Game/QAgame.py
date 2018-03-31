from aip import AipOcr
from PIL import ImageGrab
import time, requests, re
from multiprocessing.dummy import Pool
import jieba

APP_ID = '10733116'
API_KEY = 'Ns0BpieM7qOYT92R9e3ZugfQ'
SECRET_KEY = 'ggGEFuuuw0e9yRi3FyYxb5w7XR19CLTa'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

screen_shot_area = ((244, 150, 785, 415))

screen_shot_path = 'screenshot.png'

def img_read(img_path):
    with open(img_path, 'rb') as fl:
        img = fl.read()
    fl.close()
    return img

def img_ocr(img):
    content = client.basicGeneral(img)
    return content['words_result']

def threading_control(ocr_result):
    basic_url = 'http://www.baidu.com/s?wd='
    urls = [basic_url + ocr_result['question']]
    for i in ocr_result['answers']:
        urls.append(basic_url + ocr_result['question'] + ' ' + i)
    pool = Pool(4)
    html_result = pool.map(get_html, urls)
    pool.close()
    pool.join()
    return html_result

def get_html(url):
    while True:
        try:
            html = requests.get(url).text
            return html
        except:
            pass

def get_answer_basic(html, ocr_result): # ocr_result = {'question':'问题', 'answers':['1','2','3']}
    result = []
    for each_answer in ocr_result['answers']:
        # print(re.findall(each_answer.replace('(', ''), html))
        result.append({each_answer:len(re.findall(each_answer.replace('(', ''), html))})
    return result

def get_answer_append(html):
    best_result = re.findall(r'答案(.*?)\.\.\.', html)
    if best_result:
        return best_result

def deal_img_content(img_content):
    temp_content = img_content[:]
    result = {'question': '', 'answers': []}
    for each_str in img_content:
        if not re.match(r'.*?([\u4E00-\u9FA5])', each_str['words']):
            temp_content.remove(each_str)
        if each_str['words'].find('?') > 0:
            mark_index = each_str
            break
    for i in temp_content[:temp_content.index(mark_index) + 1]:
        result['question'] += i['words']
    for i in temp_content[temp_content.index(mark_index) + 1:]:
        result['answers'].append(i['words'])
    return result


def main():
    print('开始截图，进行识别')
    # 截图
    screen_shot_pic = ImageGrab.grab(screen_shot_area)
    screen_shot_pic.save(screen_shot_path)
    # 识图
    img = img_read(screen_shot_path)
    img_content = img_ocr(img)
    # 处理识图结果
    qa_dict = deal_img_content(img_content)
    print('问题\n')
    print(qa_dict['question'])
    html_result = threading_control(qa_dict)
    result_1 = get_answer_basic(html_result[0], qa_dict)
    result_2 = []
    for each_result in html_result[1:]:
        result_2.append(get_answer_append(each_result))
    return result_1, result_2

img = img_read('C:/Users\Administrator\Desktop/index.jpg')
img_content = img_ocr(img)
print(img_content)
exit()

while True:
    print('等待按键')
    a = input()
    start_time = time.time()

    result_1, result_2 = main()
    for x, y in zip(result_1, result_2):
        print(str(x))
        try:
            for i in y:
                print(i)
        except:
            pass
        print('\n')
    print('总共耗时：%s' %str(time.time()-start_time))

