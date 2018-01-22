#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by manue1 on 2017/8/7
from scrapy import Request
from scrapy.spiders import CrawlSpider


class Spider(CrawlSpider):
    name = '013_malc0de.com'
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES":{
            'opensource_threat_intel.middlewares.RandomProxyMiddleware': 1
        }
    }
    allowed_domains = [
        "malc0de.com"
    ]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'opensource_threat_intel.middlewares.RandomProxyMiddleware': 1,
            'opensource_threat_intel.middlewares.PhantomJSMiddleware': 2
        },
        "DOWNLOAD_DELAY": 0.5,
        "COOKIES_ENABLED":True
    }
    '''
     1.提供feed http://malc0de.com/bl/
     2.提供rss
     3.页面database数据最完整
    '''
    start_urls = [
        "http://malc0de.com/database/",
    ]
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Cookie": "__cfduid=d0c8b3ca7338def258884655e9681965f1497519044; _ga=GA1.2.729796356.1502086123; _gid=GA1.2.696334001.1511149894; _gat=1; __utmt=1; __utma=125106710.729796356.1502086123.1511149894.1511157949.10; __utmb=125106710.1.10.1511157949; __utmc=125106710; __utmz=125106710.1502086123.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "Host": "malc0de.com",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://malc0de.com/database/",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Remote-Address":"192.168.255.51:3128",
    }
    def start_requests(self):
        for url in self.start_urls:
            print url
            yield Request(url,headers=self.header,
                              callback=self.parse_database,
                              meta={"PhantomJS":True,
                                      "cookie":"__cfduid=d0c8b3ca7338def258884655e9681965f1497519044; _ga=GA1.2.729796356.1502086123; _gid=GA1.2.696334001.1511149894; _gat=1; __utmt=1; __utma=125106710.729796356.1502086123.1511149894.1511157949.10; __utmb=125106710.1.10.1511157949; __utmc=125106710; __utmz=125106710.1502086123.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)"}
                            )
            # yield Request(url,headers=self.header,
            #               callback=self.parse_database,
            #               )

    def parse_database(self, response):
        print response.url
        open('body.html', 'w').write(response.body)
