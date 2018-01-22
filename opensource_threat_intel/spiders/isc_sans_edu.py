# -*- coding: utf-8 -*-
import time
import re
from scrapy import Request
from scrapy.spiders import CrawlSpider

from ..items import OpensourceThreatIntelItem


class Spider(CrawlSpider):
    name = "isc.sans.edu"
    allowed_domains = ["isc.sans.edu"]
    start_urls = [
        'https://isc.sans.edu/feeds/suspiciousdomains_Low.txt',
        'https://isc.sans.edu/feeds/suspiciousdomains_High.txt',
        'https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt',
        'https://isc.sans.edu/feeds/block.txt',
    ]

    def start_requests(self):
        for url in self.start_urls:
            if url.find('block') >=0 :
                yield Request(url, callback=self.parse_1)
            else:
                yield Request(url, callback=self.parse_2)

    # item数据格式规范
    @staticmethod
    def format_data(indicator,data_type,alive_time):
        tag = 0
        item = OpensourceThreatIntelItem()
        now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        item['indicator'] = indicator
        item['data_type'] = data_type
        item['tag'] = tag
        item['alive'] = True
        item['description'] = 'none'
        item['confidence'] = 8
        item['source'] = 'isc.sans.edu'
        item['updated_time'] = alive_time
        item['created_time'] = now_time
        return item

    def parse_1(self, response):
        lines = response.body.strip().split('\n')
        content = lines[9]
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
        alive_time = content_list[10] + '-' + month[content_list[6]] + '-' + content_list[8] + 'T' + content_list[9]
        for line in lines:
            if not line.startswith('#'):
                if not line.startswith('Start'):
                    indicator = line.split('	')[0]
                    yield self.format_data(indicator,0,alive_time)

    def parse_2(self, response):
        lines = response.body.strip().split('\n')
        content = lines[8]
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
        alive_time = content_list[10] + '-' + month[content_list[6]] + '-' + content_list[8] + 'T' + content_list[9]
        for line in lines:
            if not line.startswith('#'):
                if not line.startswith('Site'):
                    yield self.format_data(line,1,alive_time)
