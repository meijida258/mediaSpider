# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse

# 引入selenium等待加载包
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from .getUserAgent import FakeChromeUA
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from sys import path
path.append('C:\ProxyPool\WebApi')
from apis import get_proxy
import redis
import random
import time
import json

from .redis_conn import get_redis_conn

class ScrapyCloudmusicSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FirefoxMiddleware(object):
    options = webdriver.FirefoxOptions()  # 指定使用的浏览器
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(5)

    @classmethod
    def process_request(self, request, spider):
        if 'firefox' in request.meta:
            try:
                js = 'window.open("{}");'.format(request.url)
                self.driver.execute_script(js)
            except:
                self.driver.get(request.url)
            windows = self.driver.window_handles
            if len(windows) >= 5: # 窗口过多，关闭之前的窗口
                self.driver.switch_to.window(window_name=windows[0])
                self.driver.close()
            self.driver.switch_to.window(window_name=windows[-1])

            WebDriverWait(driver=self.driver, timeout=3, poll_frequency=0.5).until(
                EC.presence_of_element_located((By.NAME, 'contentFrame')))
            self.driver.switch_to.frame('contentFrame')
            body = self.driver.page_source
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        else:
            return None

class MyUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', FakeChromeUA.get_ua())

class MyPorxyMiddleware():
    redis_conn = get_redis_conn(host='localhost', port=6379, db=3)
    def process_request(self, request, spider):
        # 保持redis连接
        try:
            self.redis_conn.ping()
        except:
            self.redis_conn = get_redis_conn(host='localhost', port=6379, db=3)

        # 根据代理失败次数进行判断
        if request.meta.setdefault('proxy_failed_times', 0) == 4:
            print('连续四次访问出错，不使用代理访问')
            # del request.meta['proxy']
            request.meta['proxy'] = random.choice['','http://192.168.2.100:8081']
        else:
            try:
                proxy = get_proxy(1, self.redis_conn, 4)[0]
            except:
                proxy = random.choice['','http://192.168.2.100:8081']
            time.sleep(random.uniform(0.1,0.3))
            request.meta['proxy'] = 'http://{}'.format(proxy)


class MyRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # 继承的重试middleware,用于是返回json结果的请求，检验结果，判断是否获取数据成功
        if request.meta.setdefault('json_result', False):
            try:
                response_json = json.loads(response.body_as_unicode())
            except:
                reason = response_status_message('502') # 未收到json结果，返回502错误
                request.meta['proxy_failed_times'] = 0
                return self._retry(request, reason, spider) # 重新请求
            if int(response_json['code']) == 200:
                return response
            else:
                print('json result error')
                reason = response_status_message('502') # 收到错误的json结果，返回502错误
                request.meta['proxy_failed_times'] = 0
                return self._retry(request, reason, spider) # 重新请求
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            try:
                request.meta['proxy_failed_times'] += 1
            except:
                pass
            return self._retry(request, exception, spider)