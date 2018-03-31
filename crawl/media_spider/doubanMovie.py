# -*- coding: UTF-8 -*-
import requests,re,random, time, datetime, smtplib
from pymongo import MongoClient
from lxml import etree
from multiprocessing.dummy import Pool as ThreadPool
from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.header import Header
from email.utils import parseaddr, formataddr
class Douban():
    def __init__(self):
        self.movieType = TARGET_TYPE
        self.url = 'https://movie.douban.com/tag/target?start=0&type=S'
        self.headers = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)']
        self.proxies = []
        for proxyDict in mon.proxyCollection.find():
            self.proxies.append(proxyDict['proxy'])

    def getHtml(self, url):
        linkCount = 1
        while linkCount < 10:
            time.sleep(random.uniform(0, linkCount))
            try:
                html = requests.get(url, headers={'User-Agent': self.headers[random.randint(0, len(self.headers) - 1)]},
                                    timeout=30,
                                    proxies={'http': 'http://%s' % self.proxies[random.randint(0, len(self.proxies) - 1)]}).content
                return html
            except Exception, e:
                if linkCount >= 5:
                    print e.message + '\n' + '第%s次链接失败' % linkCount
                linkCount += 1
                html = None
        return html

    def pageContent(self, html):
        selector = etree.HTML(html)
        itemClassList = selector.xpath('//*[@class="item"]')
        return itemClassList

    def mainPro(self, url):
        html = self.getHtml(url)
        result = []
        itemClassList = self.pageContent(html)
        for item in itemClassList:
            itemDict = {}
            try:
                itemDict['movieName'] = self.contentDeal(item.xpath('td[2]/div[1]/a/text()')[0])
            except IndexError:
                pass
            try:
                itemDict['moviePoints'] = item.xpath('td[2]/div[1]/div[1]/span[2]/text()')[0]
            except IndexError:
                pass
            try:
                itemDict['movieDoubanLink'] = item.xpath('td[1]/a/@href')[0]
            except IndexError:
                pass
            itemDict = self.getMovieDetail(itemDict)
            mon.insert(itemDict)

    def main(self):
        baseUrl = re.sub(r'target', TARGET_TYPE, self.url)
        urlList = []
        for page in range(0, 390):
            urlList.append(re.sub(r'start=\d+', 'start=' + str(page * 20), baseUrl))
        pool = ThreadPool(4)
        pool.map(self.mainPro, urlList)
        pool.close()
        pool.join()
        # for url in urlList:
        #     self.mainPro(url)

    def getMovieDetail(self, itemDict):
        print '获取%s的详细信息' %itemDict['movieName'].encode('utf-8')
        url = itemDict['movieDoubanLink']
        html = self.getHtml(url)
        selector = etree.HTML(html)
        movieTypeList = selector.xpath('//*[@property="v:genre"]/text()')
        movieType = '/'.join(movieTypeList)
        itemDict['movieType'] = movieType
        try:
            itemDict['movieReleaseDate'] = selector.xpath('//*[@property="v:initialReleaseDate"]/text()')[0]
        except IndexError:
            pass
        try:
            itemDict['movieSummary'] = self.contentDeal(selector.xpath('//*[@property="v:summary"]/text()')[0])
        except IndexError:
            pass
        itemDict['isWatching'] = 'No'

        return itemDict

    def contentDeal(self, contentStr):
        contentStr = re.sub(r'"', '', contentStr)
        contentStr = re.sub('\n', '', contentStr)
        contentStr = re.sub('/', '', contentStr)
        contentStr = re.sub(' ', '', contentStr)
        return contentStr
class Mongo():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.dbProxy = self.client.Proxy
        self.proxyCollection = self.dbProxy.Ip
        self.dbMovie = self.client.Douban
        self.doubanCollection = self.dbMovie.movieInfo
        self.dbWeibo = self.client.Weibo
        self.ImgCollection = self.dbWeibo.user_2527194201

    def insert(self, itemDict):
        if mon.doubanCollection.find({'movieName':itemDict['movieName']}).count() == 0:
            mon.doubanCollection.insert(itemDict)
            print '录入电影：' + str(itemDict['movieName'].encode('utf-8'))


def log(func):
    def wrapper(*args, **kw):
        print 'call: %s()' % func.__name__
        return func(*args, **kw)
    return wrapper
class MovieRandom():
    def __init__(self):
        self.movieList = mon.doubanCollection.find({'isWatching': 'No'})
        self.sender = 'meijida123@163.com'
        self.password = 'jijida258'
        self.receivers = '2517857637@qq.com'
        self.smtpSever = 'smtp.163.com'
        self.img = mon.ImgCollection.find()[random.randint(0, mon.ImgCollection.find().count() - 1)]['content']



    @ log
    def formatAddr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(),
                           addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    @ log
    def sendMail(self):
        movieAdvance = self.getMovieAdvance()
        message = MIMEMultipart()
        # message = MIMEText(self.getMovieSu(movieAdvance), 'html', 'utf-8')
        message['From'] = self.formatAddr('cjl<%s>' % self.sender)
        message['To'] = self.formatAddr('nyan<%s>' % self.receivers)

        subject = '每日电影推荐-%s' % movieAdvance['movieName'].encode('utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        content = self.getMovieSu(movieAdvance)
        content = re.sub(r'</body></html>', '\n<p><img src="cid:0"></p></body></html>', content)
        message.attach(MIMEText(content, 'html', 'utf-8'))
        # -------------------------------------- 添加附件
        mime = MIMEBase('image', self.img.split('.')[-1], filename=self.img)
        # 头信息
        mime.add_header('Content-Disposition', 'attachment', filename=self.img)
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')

        mime.set_payload(requests.get(self.img).content)
        encoders.encode_base64(mime)
        message.attach(mime)
        # -------------------------------------- 嵌入图片
        # imgContent = MIMEImage(requests.get(self.img).content)
        # imgContent.add_header('Content-ID', '<digglife>')
        # message.attach(imgContent)
        try:
            smtpObj = smtplib.SMTP(self.smtpSever, 25)
            smtpObj.login(self.sender, self.password)
            smtpObj.sendmail(self.sender, [self.receivers], message.as_string())
            print '邮件发送成功'
        except smtplib.SMTPException, e:
            print '无法发送邮件' + e.message

    def getMovieSummary(self, movieDict):
        messageText = ''
        messageText += '电影名称：' + movieDict['movieLink'].encode('utf-8') + '\n'
        messageText += '电影类型：' + movieDict['movieType'].encode('utf-8')  + '\n'
        messageText += '电影评分：' + movieDict['moviePoints'].encode('utf-8')  + '\n'
        try:
            messageText += '电影简介：' + movieDict['movieSummary'].encode('utf-8')
        except KeyError:
            pass
        return messageText

    @ log
    def getMovieSu(self, movieDict):
        messageText = '<html><body><p>'
        messageText += '电影名称：<a href="%s"' % movieDict['movieDoubanLink'].encode('utf-8')
        messageText += '>%s</a></p>\n' % movieDict['movieName'].encode('utf-8')
        messageText += '<p>电影类型：%s</p>\n' % movieDict['movieType'].encode('utf-8')
        messageText += '<p>电影评分：%s</p>\n' % movieDict['moviePoints'].encode('utf-8')
        messageText += '<p>电影简介：%s</p></body></html>' % movieDict['movieSummary'].encode('utf-8')
        return messageText

    @ log
    def getMovieAdvance(self):
        count = 1
        targetPoints = 0
        while count < 10:
            movieDict = self.movieList[random.randint(1700, self.movieList.count() - 1)] # 随机电影
            if movieDict['moviePoints'] > targetPoints:
                targetPoints = movieDict['moviePoints']
                result = movieDict
            count += 1
        return result

if __name__ == '__main__':
    TARGET_TYPE = '剧情'
    mon = Mongo()
    dou = Douban()
    adv = MovieRandom()
    adv.sendMail()
    # dou.main()

