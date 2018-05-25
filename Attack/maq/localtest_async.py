import asyncio, aiohttp
from pymongo import MongoClient
import pandas, time, numpy
from concurrent.futures._base import TimeoutError

# GET /hot_rooms?count=20&skip=0 HTTP/1.1


headers = {'Authorization': 'Token 03cd90c35c0f73fd43cf6e76c4b6154b244e69ae6fa001fa9bb903d5a55c2ec5',
            'Host': '220.166.65.195:8080',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.5.0'}

ip_proxy = {'http':'http://192.168.2.100:8081'}

# print(requests.get(top_list_url, headers=headers, proxies=ip_proxy).json())
# exit()

# 并发使用代理访问
async def my_request(r_index,log):
    async with aiohttp.ClientSession() as session:
        start_time = time.clock()
        url = 'http://220.166.65.195:8080/following_rooms?count=20'
        try:
            async with session.get(url=url,
                                   headers=headers,
                                   timeout=10,
                                   ) as response:
                result = await response.text()
                log['succeed'] = log.setdefault('succeed', 0) + 1
                # log.append({'r_index':r_index, 'starttime':start_time, 'endtime':time.clock(), 'usetime':time.clock()-start_time, 'result':result})
                print('代号{} 访问{}成功,结果：\n{}'.format(r_index, url, result))
        except TimeoutError:
            # log.append({'r_index': r_index, 'starttime': start_time, 'endtime': time.clock(),
            #             'usetime': time.clock() - start_time, 'result': '访问失败'})
            log['timeout'] = log.setdefault('timeout', 0) + 1
            print('代号{} 访问{}失败,错误：{}'.format(r_index, url, 'TimeoutError'))
        except aiohttp.client_exceptions.ServerDisconnectedError:
            log['disconnected'] = log.setdefault('disconnected', 0) + 1
            print('代号{} 访问{}失败,错误：{}'.format(r_index, url, 'ServerDisconnectedError'))
        except aiohttp.client_exceptions.ClientOSError:
            log['oserror'] = log.setdefault('oserror', 0) + 1
            print('代号{} 访问{}失败,错误：{}'.format(r_index, url, 'ClientOSError'))
        except Exception:
            log['othererrors'] = log.setdefault('othererrors', 0) + 1
            print('代号{} 访问{}失败,错误：{}'.format(r_index, url, 'Other'))
request_times = 1

log = {}
while request_times > 0:
    proxy_list = numpy.arange(500)
    # random.shuffle(proxy_list)
    loop = asyncio.get_event_loop()
    tasks = [my_request(proxy_dict+request_times*1000, log) for proxy_dict in proxy_list]
    loop.run_until_complete(asyncio.wait(tasks))
    request_times -= 1
# log_d = pandas.DataFrame(log)
# log_d.to_csv('C:/Users\Administrator\Desktop/test_log.csv')
log['total'] = 10*500
print(log)