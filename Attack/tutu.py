import asyncio, aiohttp
from pymongo import MongoClient
import random
from multiprocessing.dummy import Pool

t = '1170f864930b85834f2aa482cd1eb447df4d'
t1 = '8353dcda0ab798494302982f424e2d698fd3'
k = 'be3d8184176377538b026f9231added9'
cpsUsername = 'fm_0001'
h = '01200156fm_0001'
driveid = '868453026613028'

headers = {'User-Agent': 'okhttp/3.8.1',
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'host': '123.206.219.117',
            'k':k,
            'h':h,
            't':t,
            't1':t1,
            'driveid':driveid,
            'cpsUsername':cpsUsername}

ip_proxy = {'http':'http://192.168.2.100:8081'}

top_list_url = 'http://123.206.219.117/peipeindex/top/getlist?type={}'

# print(requests.get(top_list_url, headers=headers, proxies=ip_proxy).json())
# exit()

# 并发使用代理访问
async def my_request(proxy_dict):
    async with aiohttp.ClientSession() as session:
        url = top_list_url.format(random.choice([2, 3]))
        try:
            async with session.get(url=url,proxy='http://{}'.format(proxy_dict['proxy']),
                                   headers=headers,
                                   timeout=5,
                                   ) as response:
                # result.append({'proxy_dict': proxy_dict, 'status': response.status})
                result = await response.json()
                print('代理http://{} 访问{}成功,结果：\n{}'.format(proxy_dict['proxy'],url, result))
        except Exception as e:
            print('代理http://{} 访问{}失败,错误为：\n{}'.format(proxy_dict['proxy'], url, e.args))

request_times = 1

client = MongoClient('localhost', 27017)
db = client.Proxy
collection = db.UsefulProxy
proxy_list = list(collection.find({}, {'proxy':1, '_id':0}))

while request_times > 0:
    random.shuffle(proxy_list)
    loop = asyncio.get_event_loop()
    tasks = [my_request(proxy_dict) for proxy_dict in proxy_list]
    loop.run_until_complete(asyncio.wait(tasks))
    request_times -= 1
