import aiohttp, requests
import asyncio
import async_timeout
import queue
from ProxyMantenance import prou
from lxml import etree
import time
def proxy_queue():
    # 定义一个代理的队列
    proxy_list = prou.get_all_proxy('http')
    q = queue.Queue(maxsize=0)
    for proxy in proxy_list:
        q.put(proxy)
    return q
async def get_page(url, page_urls):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 200
            page_urls.append(await response.text())
            html = etree.HTML(await response.text())
            for i in html.xpath('//*[@class="paginator"]/a/@href'):
                page_urls.append('https://movie.douban.com/top250' + i)

async def fetch(session, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            print(await resp.text())

async def main(loop):
    proxy = prou.get_random_proxy('http')
    async with aiohttp.ClientSession(loop=loop) as session:
        html = await fetch(session, 'http://www.7kk.com')
        print(html)



def parse_item(html):
    xpath_html = etree.HTML(html)
    movie_list = xpath_html.xpath('span[@class="title"]/text()')
    return movie_list

st = time.time()
page_htmls = []
loop = asyncio.get_event_loop()
loop.run_until_complete(get_page('https://movie.douban.com/top250', page_htmls))

page_urls = ['https://movie.douban.com/top250?start=0&filter=', ]
for html in page_htmls:
    html_xpath = etree.HTML(html)
    for i in html_xpath.xpath('//*[@class="paginator"]/a/@href'):
        page_urls.append('https://movie.douban.com/top250' + i)
# for page in page_urls:
#     a = requests.get(page).content
# print(time.time() - st)
movie_reps = []
tasks = [get_page(page, movie_reps) for page in page_urls]
loop.run_until_complete(asyncio.wait(tasks))

movie_result = []
for movie_rep in movie_reps:
    html = etree.HTML(movie_rep)
    for movie_title in html.xpath('//span[@class="title"][1]/text()'):
        movie_result.append(movie_title)
loop.close()

for i in movie_result:
    print(i + '-----' + str(movie_result.index(i)))
print(time.time() - st)