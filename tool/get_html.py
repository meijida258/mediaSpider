# -*- coding: UTF-8 -*-
import requests, random, time
from fake_useragent import UserAgent

class HtmlPro:
    def get_headers(self):
        headers_dict = {}
        headers_dict['User-Agent'] = str(ua_.random)
        return headers_dict

    def get_html(self, url, proxies=None, timeout=None, retry_time=None):
        if not retry_time:
            retry_time = 1
        time.sleep(retry_time * 1)
        link_time = 1
        while link_time <= retry_time:
            try:
                html = requests.get(url, headers=self.get_headers(), proxies=proxies, timeout=timeout)
                return html
            except Exception:
                if link_time < retry_time:
                    print ('第%s次连接出错，等待重试' % str(link_time))
                    link_time += 1
                elif link_time == retry_time:
                    print('超出重试次数，无法连接')

if __name__ == '__main__':
    hp = HtmlPro()
    ua_ = UserAgent()

else:
    hp = HtmlPro()
    ua_ = UserAgent()