# encoding:utf-8
import scrapy
import re
from SogouSpider.items import SogouspiderItem
import urllib
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class Sogou(scrapy.Spider):
    name = "Sogou"
    allowed_domains = ["www.sogou.com"]
    words = ["周奇"]
    start_urls = []
    for word in words:
        #url = 'http://www.sogou.com/web?query=%s&sourceid=&_ast=1268620800&_asf=www.sogou.com&w=01029901&num=10&p=40040100&dp=1' % urllib.quote(word)
        url = 'https://www.sogou.com/web?query=%s&sourceid=&_asf=www.sogou.com&ie=utf8' % urllib.quote(
            word)
        print url
        start_urls.append(url)

    def __init__(self):
        self.count = 0

    def __get_url_query(self, url):
        m = re.search("query=([^&]*)", url).group(1)
        return m

    def start_requests(self):
        for u in self.start_urls:
            #yield scrapy.Request(u, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
            yield scrapy.Request(u, callback=self.parse, errback=self.errback_httpbin)

    def parse(self, response):
        self.count += 1
        items = SogouspiderItem()
        xx = u"[\u4e00-\u9fa5]+"
        pattern = re.compile(xx)
        query = urllib.unquote(self.__get_url_query(response.url))
        for t in response.xpath('//div[@class="results"]/div'):
            items['title'] = (
                ''.join((''.join(t.xpath('./h3/a//text()').extract()).split()))).encode('utf-8')
            # print items['title']
            items['url'] = t.xpath('./h3/a/@href').extract()[0].encode('utf-8')
            items['content'] = (' '.join(pattern.findall(''.join(t.xpath(
                './/div[not(@style="display:none")]//text()').extract())))).encode('utf-8')
            items['word'] = query
            yield items

        nextpage = u'下一页'
        url = response.xpath(
            "//a[contains(text(),'%s')]/@href" % (nextpage)).extract()
        if url and self.count <= 10:
            page = "http://www.sogou.com/web" + url[0]
            # 获得重定向的情况。。。
            yield scrapy.Request(page, callback=self.parse, errback=self.errback_httpbin)

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            print response.url
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


    def closed_count(self):
        self.count = 0
