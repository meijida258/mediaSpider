# -*- coding: UTF-8 -*-
import requests,re,random, time, datetime, xlwt, urllib2, urllib
from pymongo import MongoClient
from lxml import etree
from multiprocessing.dummy import Pool as ThreadingPool

class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.bookDb = self.client.Douban
        self.bookCollection = self.bookDb.Book

        self.proxyDb = self.client.Proxy
        self.proxyCollection = self.proxyDb.Ip

        self.proxies = []
        for ip in self.proxyCollection.find():
            self.proxies.append(ip['proxy'])

    def insertBook(self, book_all_info):
        if self.bookCollection.find({'name':book_all_info['name']}).count() == 0:
            self.bookCollection.insert(book_all_info)

    def writeExc(self):
        w = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = w.add_sheet('book', cell_overwrite_ok=True)
        book_dir = self.bookCollection.find()
        row = 1
        for book in book_dir:
            sheet.write(row,0, book['name'])
            sheet.write(row,1, book['author'])
            sheet.write(row,2, book['tags'])
            sheet.write(row,3, book['description'])
            sheet.write(row,4, book['download'])
            row += 1
        w.save('123.xls')
class Book():
    def __init__(self):
        self.book_tag = ''
        self.base_url = 'https://book.douban.com/tag/'
        self.headers = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)']

    def getHtml(self, url):
        count = 1
        while True:
            proxies = mon.proxies[random.randint(0, len(mon.proxies) - 1)]
            try:
                time.sleep(random.uniform(3 * count, 5 * count))
                html = requests.get(url, headers={'User-Agent':self.headers[random.randint(0, len(self.headers) - 1)],
                                                  'Host':'book.douban.com'}, proxies={'http': 'http://%s' % proxies},
                                     timeout=30).content
                if html.find('403 Forbidden') < 0:
                    return html
                else:
                    print '403 Forbidden'
            except Exception, e:
                count += 1
                print '使用代理：%s获取：%s错误为：%s' % (str(proxies), url, e.args)

    def getPageBookLink(self, url):
        print url
        html = self.getHtml(url)
        book_links = re.findall(r'<a href="(https://book\.douban\.com/subject/\d+/)" title=', html)
        if book_links:
            return book_links


    def getBookInfo(self, book_links):
        for book_link in book_links:
            book_all_info = {}
            book_link_html = self.getHtml(book_link)
            print book_link
            selector = etree.HTML(book_link_html)
            book_all_info['description'] = self.getBookDes(book_link_html)
            book_all_info['tags'] = self.getBookTags(book_link_html)
            try:
                book_all_info['auther'] = selector.xpath('//*[@id="info"]/span/a/text()')[0]
            except IndexError:
                book_all_info['auther'] = '暂无or未查到'
            try:
                book_all_info['evaluate'] = selector.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()')[0]
            except IndexError:
                book_all_info['evaluate'] = '暂无or未查到'
            try:
                book_all_info['name'] = selector.xpath('//*[@id="wrapper"]/h1/span/text()')[0]
            except IndexError:
                book_all_info['name'] = '暂无or未查到'
            mon.insertBook(book_all_info)

    def getBookTags(self, book_link_html):
        selector = etree.HTML(book_link_html)
        try:
            a = selector.xpath('//*[@id="db-tags-section"]/div')[0]
            tags = a.xpath('string()')
            tags = tags.replace('\n', '')
            tags = tags.replace(' ', '')
            return tags
        except IndexError:
            return '暂无or未查到'

    def getBookDes(self, book_link_html):
        selector = etree.HTML(book_link_html)
        try:
            b = selector.xpath('//*[@id="link-report"]/span[1]/div')[0]
            description = b.xpath('string()')
            description = description.replace('\n', '')
            return description
        except IndexError:
            return '暂无or未查到'
    def getPageUrl(self):
        page_urls = []
        for page in range(22, 50):
            url = self.base_url + self.book_tag + '?start=%s&type=S' % str(page*20)
            page_urls.append(url)

        return page_urls

    def getAllBook(self, url):
        pageBookLinks = self.getPageBookLink(url)
        self.getBookInfo(pageBookLinks)

    def main(self):
        page_urls = self.getPageUrl()
        pool = ThreadingPool(4)
        pool.map(self.getAllBook, page_urls)
        pool.close()
        pool.join()


if __name__ == '__main__':
    book = Book()
    mon = Mongo()
    # book.main()
    # mon.writeExc()

