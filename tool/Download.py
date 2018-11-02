# -*- coding: UTF-8 -*-
import asyncio
import aiohttp
import os
import web
from pymongo import MongoClient

class DownLoad():
    def __init__(self, url_list, save_path, proxies_list):
        self.url_list = url_list
        self.save_path = save_path
        self.proxies_list = proxies_list

    def save_download(self, name, url, data):
        try:
            suffix = url.split('.')[-1]
        except IndexError:
            suffix = 'jpg'
        with open('{path}/{name}.{suffix}'.format(path=self.save_path, name=name, suffix=suffix), 'wb') as fl:
            fl.write(data)

    async def http_get(self, session, url):
        try:
            async with session.get(url) as response:
                res = await response.read()
                return res
        except Exception as exc:
            raise web.HTTPError

    async def download_one(self, url, name, session):
        try:
            data = await self.http_get(session, url)
        except web.HTTPError:
            return {'url':url, 'result':'request failed'}
        else:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None,
                                 self.save_download,
                                 name, url, data)
            return {'url':url, 'result':'succeed'}

    async def download_many(self, url, name, session, sem):
        async with sem:
            result = await self.download_one(url, name, session)
            return result
    async def download_main(self):
        sem = asyncio.Semaphore(500)
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(self.download_many(url, name, session, sem)) for name, url in enumerate(self.url_list)]
            result = await asyncio.gather(*tasks)
            return result
    def main(self):
        self.loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.download_main())
        result = self.loop.run_until_complete(future)
        return result

