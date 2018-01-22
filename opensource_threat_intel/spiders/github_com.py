# -*- coding: utf-8 -*-
# from first.items import FirstItem
import time
import re
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from ..items import OpensourceThreatIntelItem
from scrapy.linkextractors import LinkExtractor
from IPy import IP
from scrapy.selector import Selector

class Spider(CrawlSpider):
    name = "github.com"
    allowed_domains = ["github.com"]
    start_urls = [  
        'https://github.com/firehol/blocklist-ipsets',       
    ]
    rules = (
        Rule(LinkExtractor(allow='/blob/master/[^A-Z]'),callback="parse_3",follow=True),
        )
    
    def parse_3(self, response):
        tag = 5
        data_type = 0
        sel = Selector(response)
        trs = sel.xpath('//*[@itemprop="text"]/table[@class="highlight tab-size js-file-line-container"]/tr')
        for i in range(0,len(trs)):
            item = OpensourceThreatIntelItem()
            tr = trs[i]  
            content = tr.xpath('string(td[2])')[0].extract().strip()
            if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{2}', content):
                ipList = IP(content)
                for ip in ipList:
                    item['indicator'] = str(ip)
                    now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
                    item['data_type'] = data_type
                    item['tag'] = tag
                    item['alive'] = False
                    item['description'] = 'none'
                    item['confidence'] = 5
                    item['source'] = 'github.com'
                    item['updated_time'] = 'none'
                    item['created_time'] = now_time
                    yield item

            elif re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',content):
                ip = content
                item['indicator'] = ip
                now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
                item['data_type'] = data_type
                item['tag'] = tag
                item['alive'] = False
                item['description'] = 'none'
                item['confidence'] = 5
                item['source'] = 'github.com'
                item['updated_time'] = 'none'
                item['created_time'] = now_time
                yield item
            else:
                item['indicator'] = content
                now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
                item['data_type'] = data_type
                item['tag'] = tag
                item['alive'] = False
                item['description'] = 'none'
                item['confidence'] = 5
                item['source'] = 'github.com'
                item['updated_time'] = 'none'
                item['created_time'] = now_time
                yield item