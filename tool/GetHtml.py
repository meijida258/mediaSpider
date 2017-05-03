# -*- coding: UTF-8 -*-
import requests, random, time
from fake_useragent import UserAgent

class HtmlPro:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language': 'en',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        }
    def get_headers(self):
        headers_dict = self.headers
        headers_dict['User-Agent'] = str(ua_.random)
        return headers_dict

    def get_html(self, url, proxies=None, timeout=30, referer=None,retry_time=None, random_ua=False):
        if not retry_time:
            retry_time = 1
        # 随机ua
        if random_ua:
            headers = self.get_headers()
        else:
            headers = self.headers
        if referer:
            headers['Referer'] = referer
        time.sleep(retry_time * 1)
        link_time = 1
        while link_time <= retry_time:
            try:
                html = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
                return html # 未确定格式的response
            except Exception:
                if link_time < retry_time:
                    print ('第%s次连接出错，等待重试' % str(link_time))
                    link_time += 1
                elif link_time == retry_time:
                    print('超出重试次数，无法连接')
                    return ''
if __name__ == '__main__':
    hp = HtmlPro()
    ua_ = UserAgent()

else:
    hp = HtmlPro()
    ua_ = UserAgent()