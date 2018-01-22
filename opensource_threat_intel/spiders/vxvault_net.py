# -*- coding: utf-8 -*-
import time
import re
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import OpensourceThreatIntelItem
from scrapy import Selector

class Spider(CrawlSpider):
    name = "vxvault.net"
    allowed_domains = ["vxvault.net"]
    start_urls = [
        'http://vxvault.net/ViriList.php',       
        'http://vxvault.net',
        'http://vxvault.net/URL_List.php',      
    ]    
    rules = (
        Rule(LinkExtractor(allow='ViriList.php\S*'),callback='parse_2',follow=True),
        Rule(LinkExtractor(allow='URL_List.php'),callback='parse_1',follow=True),
    )
            
    def parse_2(self, response):
        tag = 10
        sel = Selector(response)
        trs = sel.xpath('//*[@id="page"]/table/tr')
        print trs
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[1])')[0].extract().strip()
            now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
            content_list = now_time.split('-')
            alive_time = content_list[0] + '-' + content + 'T' + '00:00:00'
            url = tr.xpath('string(td[2]/a[2])')[0].extract().strip()
            md5 = tr.xpath('string(td[3])')[0].extract().strip()
            ip = tr.xpath('string(td[4])')[0].extract().strip()
            
            #ip作为ID
            item = OpensourceThreatIntelItem()
            data_type = 0
            item['indicator'] = ip
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = url
            item['confidence'] = 5
            item['source'] = 'vxvault.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item
            
            #url作为ID
            item = OpensourceThreatIntelItem()
            data_type = 2
            item['indicator'] = url
            item['data_type'] = data_type
            item['tag'] = tag
            item['alive'] = True
            item['description'] = ip
            item['confidence'] = 5
            item['source'] = 'vxvault.net'
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
            item['description'] = ip
            item['confidence'] = 5
            item['source'] = 'vxvault.net'
            item['updated_time'] = alive_time
            item['created_time'] = now_time
            yield item
            
    def parse_1(self, response):
        tag = 7
        data_type = 2
        lines = response.body.split('\n')
        content = lines[2]
        content_list = content.split(' ')
        month = {
                'Jan': '01',
                'Feb': '02',
                'Mar': '03',
                'Apr': '04',
                'May': '05',
                'Jun': '06',
                'Jul': '07',
                'Aug': '08',
                'Sep': '09',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12',
            }
        for line in lines:
            if str.startswith(line, 'http'):
                if line:
                    item = OpensourceThreatIntelItem()
                    url = line.split(' ')[0].strip()
                    alive_time = content_list[3] + '-' + month[content_list[2]] + '-' + content_list[1] + 'T' + content_list[4]
                    now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
                    item['indicator'] = url
                    item['data_type'] = data_type
                    item['tag'] = tag
                    item['alive'] = True
                    item['description'] = 'none'
                    item['confidence'] = 10
                    item['source'] = 'vxvault.net'
                    item['updated_time'] = alive_time
                    item['created_time'] = now_time
                    yield item 
