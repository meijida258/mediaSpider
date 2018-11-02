import aiohttpServer, asyncio

async def get_one(url, session, result):
    print(session)
    async with session.get(url) as res:
        res_ = await res.read()
        res_code = res.status
        result.append(res_)
        return res_code

async def get_amount(sem, url,session, result):
    async with sem:
        return await get_one(url, session, result)
async def main(date_list, result):
    sem = asyncio.Semaphore(5)
    async with aiohttpServer.ClientSession() as session:
        tasks = [asyncio.ensure_future(get_amount(sem, 'http://www.acfun.cn', session, result)) for i in range(date_list)]
        # result = await asyncio.wait(*tasks)
        responses = await asyncio.gather(*tasks)
base_url = 'http://127.0.0.1:24423/{}'

loop = asyncio.get_event_loop()
result = []
future = asyncio.ensure_future(main(10, result))
res = loop.run_until_complete(future)
print(res)