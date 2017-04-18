import sys, re
from lxml import etree
sys.path.append('C:/python_practice/tool')
from get_html import hp
class Porn:
    def __init__(self):
        block_head_list = ["dushijiqing", "jiatingluanlun", "yinqijiaohuan",
                           "gudianwuxia", "xiaoyuanchunse", "changpianlianzai",
                           "huangsexiaohua", "qiangjianxilie"]
    def get(self, type, page, num):
        if page == 1:
            page_url = 'http://www.88langke.com/se/{}/'.format(type)
        else:
            page_url = 'http://www.88langke.com/se/{}/index_{}.html'.format(str(type), str(page))
        html = hp.get_html(page_url).text
        result = re.findall(r'<li><a href="(/se/%s/\d+.html)" target="_blank" title="(.*?)"><span>' % type, html)

        if num <= len(result):
            num_ = num
        else:
            num_ = 0
        content = hp.get_html('http://www.88langke.com' + result[num_ - 1][0]).content
        html = etree.HTML(content)
        txt =''.join(html.xpath('//*[@class="novelContent"]/table/tbody/tr/td/text()'))
        return txt

if __name__ == '__main__':
    porn = Porn()
else:
    porn = Porn()
