import requests, json
import asyncio, aiohttp
from pymongo import MongoClient
import random

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

ip_proxy = {'http':'http://218.59.139.238:8090'}

# top_list_url = 'http://123.206.219.117/peipeindex/top/getlist?type=3'
url = 'http://www.acfun.cn/'
async def my_request(proxy_dict):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url,
                                   proxy='http://{}'.format(proxy_dict['proxy']),
                                   timeout=10,
                                   ) as response:
                # result.append({'proxy_dict': proxy_dict, 'status': response.status})
                print('代理:{} 访问结果{}'.format(proxy_dict['proxy'], response))
        except Exception as e:
            print(e)
            print('代理:{} 访问失败，原因{}'.format(proxy_dict['proxy'], e))

request_times = 1

client = MongoClient('localhost', 27017)
db = client.Proxy
collection = db.UsefulProxy
proxy_list = list(collection.find({}, {'proxy':1, '_id':0}))[-10:-8]

while request_times > 0:
    # random.shuffle(proxy_list)
    loop = asyncio.get_event_loop()
    tasks = [my_request(proxy_dict) for proxy_dict in proxy_list]
    loop.run_until_complete(asyncio.wait(tasks))
    request_times -= 1
