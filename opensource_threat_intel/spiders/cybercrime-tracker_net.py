# -*- coding: utf-8 -*-
import time
from scrapy import Selector
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import OpensourceThreatIntelItem
import time
import re

class Spider(CrawlSpider):
    name = "029_cybercrime-tracker.net"
    allowed_domains = ["cybercrime-tracker.net"]
    start_urls = [
        'http://cybercrime-tracker.net',
        'http://cybercrime-tracker.net/ccam.php',
    ]
    rules = (
        Rule(LinkExtractor(allow='index.php\S+'),callback='parse_2',follow=True),
        Rule(LinkExtractor(allow='ccam.php'),callback='parse_1',follow=True),
    )
    def parse_1(self, response):
        tag = 10
        sel = Selector(response)
        trs = sel.xpath('//*[@height="85"]/tbody/tr[@class="monitoring"]')
        for i in range(0,len(trs)):           
            tr = trs[i]
            content = tr.xpath('string(td[2])')[0].extract().strip()
            content_list = content.split(' ')
            content_list_num = content_list[0].split('/')
            alive_time = content_list_num[2] + '-' + content_list_num[1] + '-' + content_list_num[0] + 'T' + content_list[1]
            indicator = tr.xpath('string(td[3])')[0].extract().strip()
            md5 = tr.xpath('string(td[4])')[0].extract().strip()
            now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))

            #ip和domain作为ID
            item = OpensourceThreatIntelItem()
            if re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', indicator):
                data_type = 0
            else:
                data_type = 1
            item['indicator'] = indicator
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = md5
            item['confidence'] = 5
            item['source'] = 'cybercrime-tracker.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item

            #md5作为ID
            item = OpensourceThreatIntelItem()
            data_type = 3
            item['indicator'] = md5
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = indicator
            item['confidence'] = 5
            item['source'] = 'cybercrime-tracker.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item

    def parse_2(self, response):
        sel = Selector(response)
        trs = sel.xpath('//*[@class="ExploitTable"]/tbody/tr')
        for i in range(0,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[1])')[0].extract().strip()
            content_list = content.split('-')
            alive_time = content_list[2] + '-' + content_list[1] + '-' + content_list[0] + 'T' + '00:00:00'
            url = tr.xpath('string(td[2])')[0].extract().strip()
            ip = tr.xpath('string(td[3])')[0].extract().strip()
            now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))

            #ip作为ID
            item = OpensourceThreatIntelItem()
            data_type = 0
            tag = 10
            item['indicator'] = ip
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = url
            item['confidence'] = 5
            item['source'] = 'cybercrime-tracker.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item

            #url作为ID
            item = OpensourceThreatIntelItem()
            data_type = 2
            tag = 0
            item['indicator'] = url
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = ip
            item['confidence'] = 5
            item['source'] = 'cybercrime-tracker.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item
