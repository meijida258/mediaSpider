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
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(30)

    @classmethod
    def process_request(self, request, spider):
        if 'firefox' in request.meta:
            # self.driver.implicitly_wait(30)
            self.driver.get(request.url)
            self.driver.switch_to.frame('contentFrame')
            body = self.driver.page_source
            try:
                js = 'window.open("{}");'.format(request.url)
                self.driver.execute_script(js)
            except:
                self.driver.get(request.url)
            windows = self.driver.window_handles
            self.driver.switch_to.window(window_name=windows[-1])
            # driver.switch_to.frame('contentFrame')
            WebDriverWait(driver=self.driver, timeout=20, poll_frequency=0.5).until(
                EC.presence_of_element_located((By.NAME, 'contentFrame')))
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        else:
            return None
