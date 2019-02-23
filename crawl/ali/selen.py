from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import tkinter as tk

def get_standard():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    standard_url = 'https://consumeprod.alipay.com/record/standard.htm'
    driver.get(standard_url)
    time.sleep(2)
    element = driver.find_element_by_class_name('barcode')
    driver.save_screenshot('screenshot.png')
    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']
    width, height = element.size['width'], element.size['height']
    driver.close()
    im = Image.open('screenshot.png')
    im = im.crop((left, top, right, bottom))
    im.save('screenshot.png')
    return width, height
    # im.save('screenshot.png')
    # driver.close()
    #
    # while True:
    #     print('验证是否登录')
    #     if '我的账单' in driver.title:
    #         cookie = driver.get_cookies()
    #         print('成功获取cookies')
    #         break
    #     else:
    #         time.sleep(2)
    # for i in range(2):
    #     print(driver.page_source)
    #     time.sleep(15)
    # driver.close()
# get_standard()

def img_show():
    width, height = get_standard()
    root = tk.Toplevel()
    root.title('111')
    img_png = tk.PhotoImage(file='screenshot.png')
    label_img = tk.Label(root, image=img_png)
    label_img.pack()
    root.mainloop()
img_show()

