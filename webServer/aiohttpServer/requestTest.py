import asyncio, aiohttp
import random
import time

aioServerUrl = 'http://127.0.0.1:2384?cal={}'
httpBaseServerUrl = 'http://127.0.0.1:24423/{}'

async def get_one(session, url):
    try:
        async with session.get(url) as resp:
            result = await resp.read()
    except Exception:
        result = -1
    return result

async def get_amount(sem, session, url):
    async with sem:
        return await get_one(session, url)

async def get_main():
    sem = asyncio.Semaphore()
    async with aiohttp.ClientSession() as session:
        futures = [asyncio.ensure_future(get_amount(sem, session, aioServerUrl.format(random.randint(1,10000)))) for i in range(1000)]
        result = await asyncio.gather(*futures)
    return result

if __name__ == '__main__':
    st = time.clock()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_main())
    res = loop.run_until_complete(future)
    print(res)
    print(time.clock() - st)