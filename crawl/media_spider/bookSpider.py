# -*- coding: UTF-8 -*-
import requests,re,random, time, datetime, xlwt, urllib2
from pymongo import MongoClient
from lxml import etree
from multiprocessing.dummy import Pool as ThreadingPool

class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.bookDb = self.client.BookBao
        self.bookCollection = self.bookDb.Book

        self.bookIdCollection = self.bookDb.BookId

        self.proxyDb = self.client.Proxy
        self.proxyCollection = self.proxyDb.Ip

        self.proxies = []
        for ip in self.proxyCollection.find({'canVisit':'bookbao'}):
            self.proxies.append(ip['proxy'])

    def insertBook(self, book_all_info):
        if self.bookCollection.find({'name':book_all_info['name']}).count() == 0:
            self.bookCollection.insert(book_all_info)
            print '录入图书'

    def insertBookId(self, book_ids):
        for bookId in book_ids:
            if self.bookIdCollection.find({'id': bookId}).count() == 0:
                bookid_dict = {}
                bookid_dict['id'] = bookId
                self.bookIdCollection.insert(bookid_dict)
                print '录入图书id'

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
        self.book_tag = '耽美'
        self.base_url = 'http://m.bookbao.net/booklist-p_page-c_6-o_0.html'
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
            try:
                proxies = mon.proxies[random.randint(0, len(mon.proxies) - 1)]
                time.sleep(random.uniform(10, 15))
                html = requests.get(url, headers={'User-Agent':self.headers[random.randint(0, len(self.headers) - 1)],
                                                  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'},
                                    proxies={'http':'http://%s' %str(proxies)},
                                     timeout=15).content
                if html.find('书包网') > 0:
                    return html
                else:
                    print '403 Forbidden'
            except Exception, e:
                count += 1
                if count % 4 == 0:
                    time.sleep(random.uniform(10, 15))
                    try:
                        html = requests.get(url, headers={'User-Agent': self.headers[random.randint(0, len(self.headers) - 1)],
                                                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'},
                                            timeout=15).content
                        if html.find('书包网') > 0:
                            return html
                    except Exception:
                        pass
                print '链接失败，错误为：%s' %e.args
    def getBookId(self, page_url):
        while True:
            # proxies = mon.proxies[random.randint(0, len(mon.proxies) - 1)]
            html = self.getHtml(page_url)
            selector = etree.HTML(html)
            pageBookIds = []

            for each_li in selector.xpath('//*[@class="am-list-news-bd"]/ul/li/a/@href'):
                pageBookIds.append(each_li)
            if pageBookIds:
                return pageBookIds
            else:
                print '未获取到本页图书IDs'
    def getPageList(self, tag, start_page, end_page):
        page_list = []
        for page in range(start_page, end_page):
            url = self.base_url.replace('page', str(page))
            page_list.append(url)
        return page_list

    def getBookInfo(self, bookId):
        print '获取%s信息' % str(bookId)
        time.sleep(2)
        book_all_info = {}
        bookInfoUrl = 'http://m.bookbao.net' + bookId
        while True:
            html = self.getHtml(bookInfoUrl)
            selector = etree.HTML(html)
            book_all_info['tag'] = self.book_tag
            try:
                book_all_info['name'] = selector.xpath('//*[@class="am-list-main"]/h3/a/text()')[0]
                break
            except IndexError:
                print '未获取到图书名称，重新获取%s' % str(bookId)
        try:
            author = selector.xpath('//*[@class="am-list-main"]/p[1]/text()')[0]
            book_all_info['author'] = author.replace('"', '')
        except IndexError:
            book_all_info['author'] = '获取失败'
        try:
            book_type =  selector.xpath('//*[@class="am-list-main"]/p[3]/text()')[0]
            book_all_info['size'] = book_type.replace('"', '')
        except IndexError:
            book_all_info['size'] = '连载中'
        try:
            book_type = selector.xpath('//*[@class="am-list-main"]/p[5]/text()')[0]
            book_all_info['type'] = book_type.replace('"', '')
        except IndexError:
            book_all_info['type'] = '完结'
        try:
            lastUpdate = selector.xpath('//*[@class="am-list-main"]/p[4]/text()')[0]
            book_all_info['lastUpdate'] = lastUpdate.replace('"', '')
        except IndexError:
            book_all_info['lastUpdate'] = '暂无更新'
        try:
            description = selector.xpath('//*[@class="content"]/text()')[0]
            description = description.replace('/n', ';')
            book_all_info['description'] = description
        except IndexError:
            book_all_info['description'] = '暂无描述'
        return book_all_info

    def getBookDownloadLink(self, bookId, book_all_info):
        print '获取%s下载链接' % str(bookId)
        time.sleep(2)
        down_id = bookId.replace('book', 'down')
        url = 'http://m.bookbao.net' + down_id
        html = self.getHtml(url)
        try:
            downloadLink1 = re.findall(r'<li class="am-g" onclick="javascript:dl\(\'(.*?)\',1\)', html)[0]
        except IndexError:
            downloadLink1 = '未找到下载'
        try:
            downloadLink2 = re.findall(r'<li class="am-g" onclick="javascript:dl\(\'(.*?)\',2\)', html)[0]
        except IndexError:
            downloadLink2 = '未找到下载'
        try:
            downloadLink3 = re.findall(r'<li class="am-g" onclick="javascript:dl\(\'(.*?)\',3\)', html)[0]
        except IndexError:
            downloadLink3 = '未找到下载'
        book_all_info['downloadLink1'] = 'http://down1.bookbao.net:81/dl.aspx?id=X' + downloadLink1
        book_all_info['downloadLink2'] = 'http://down2.bookbao.net:81/dl.aspx?id=X' + downloadLink2
        book_all_info['downloadLink3'] = 'http://down3.bookbao.net:81/dl.aspx?id=X' + downloadLink3
        return book_all_info

    def mainPro(self, page_url):
        print '获取%s' % page_url
        pageBookIds = self.getBookId(page_url)
        mon.insertBookId(pageBookIds)

    def new_mainPro(self, bookId):
        print '获取%s' % str(bookId)
        book_all_info = self.getBookInfo(bookId)
        book_all_info = self.getBookDownloadLink(bookId, book_all_info)
        mon.insertBook(book_all_info)
        mon.bookIdCollection.remove({'id':bookId})

    def main(self):
        tag = self.book_tag
        start_page, end_page = 32, 100
        page_list = self.getPageList(tag, start_page, end_page + 1)

        for page in page_list:
            self.mainPro(page)

    def new_main(self):
        bookId_dirs = mon.bookIdCollection.find()[:50]
        bookIds = []
        for book_dir in bookId_dirs:
            bookIds.append(str(book_dir['id']))
        pool = ThreadingPool(4)
        pool.map(self.new_mainPro, bookIds)
        pool.close()
        pool.join()
        # for id in bookIds:
        #     self.new_mainPro(id)



if __name__ == '__main__':
    book = Book()
    mon = Mongo()
    book.main()
    # book.new_main()

