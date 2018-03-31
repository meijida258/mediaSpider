import sys, re
from lxml import etree
sys.path.append('C:/python_practice/tool')
from get_html import hp
html = hp.get_html('http://www.88langke.com/se/gudianwuxia/').text
result = re.findall(r'<li><a href="(/se/gudianwuxia/\d+.html)" target="_blank" title="(.*?)"><span>', html)
for i in result:
    url = 'http://www.88langke.com' + i[0]
    content = hp.get_html(url).content.decode('utf-8')
    html = etree.HTML(content)
    print(html.xpath('//*[@class="novelContent"]/table/tbody/tr/td/text()'))
