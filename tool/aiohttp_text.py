# import urllib.request as request
# from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import asyncio
import aiohttp
import time
from lxml import etree

class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Proxy
        self.collection = self.db.UsefulProxy
        self.proxy = []
        for i in self.collection.find({'type':'http'.upper()}):
            self.proxy.append('http://' + i['proxy'])

async def get_page(url, proxy, result):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, proxy=proxy, timeout=30) as response:
                result.append(response.status)
        except Exception as e:
            result.append(10060)

if __name__ == '__main__':
    mon = Mongo()
    print(len(mon.proxy))
    st = time.time()
    loop = asyncio.get_event_loop()
    # result_type()
    result = []
    tasks = [get_page('http://1212.ip138.com/ic.asp', proxy, result) for proxy in mon.proxy]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    print(time.time() - st)
    for i in result:
        print(i)
        print('*******')

