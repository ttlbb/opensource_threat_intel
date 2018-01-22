# -*- coding: utf-8 -*-
import json

from scrapy import Request
from scrapy.spiders import CrawlSpider



class ExpireddomainsSpider(CrawlSpider):
    name = "xforce"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'opensource_threat_intel.middlewares.RandomProxyMiddleware': 1
        }
    }

    allowed_domains = ["xforce.ibmcloud.com"]
    start_urls =[
        "https://api.xforce.ibmcloud.com/ipr/history/82.200.247.240"
    ]
    header = {'x-ui':'XFE'}
    def start_requests(self):
        urls = []
        with open('ip_list','r') as f :
            for line in f :
                url =  'https://api.xforce.ibmcloud.com/ipr/history/' +line.strip(),
                urls.append(url[0])
        for url in urls:
        # for url in self.start_urls:
            print url
            yield Request(url, headers=self.header, callback=self.parse_1)

    @staticmethod
    def parse_1(response):
        data = json.loads(response.body)
        ip = data['ip']
        history = data['history']
        line = ip + '\t'
        for his in history:
            cats = '|'.join(his['cats'].keys())
            create_time = his['created']
            score = his['score']
            line = line + json.dumps({"cats":cats,"create_time":create_time,'score':score})
        open('result.txt','a').write(line + '\n')



