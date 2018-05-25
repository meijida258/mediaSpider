import requests
import time

headers = {'Host': 'live-api.goddess021.com',
            'Connection': 'Keep-Alive',
           'Accept-Language':'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; unknown Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
           'Content-Type': 'application/json;charset=utf-8'}
url = 'http://live-api.goddess021.com/user/keywordSearch'
data = {"timestamp":str(int(time.time()*1000)),"sign":"6AAB83E9AEFE472A31DE350D0C5BEE4E","os":"1","udid":"868453026613028","channel":"baidu","token":"zvGQDewNfYEHKvVMzhVsDSc1dyiRhJin4FdpGxsv8jNgsJq/0m9vxEA1khlRKBSU","keyword":"A"}
response = requests.post(url, headers=headers, data=data, proxies={'http':'http://171.10.31.74:8080'}, timeout=30)
print(response.json())
