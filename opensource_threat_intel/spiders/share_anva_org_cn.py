# -*- coding: utf-8 -*-
import time
import re
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import OpensourceThreatIntelItem
from scrapy import Selector
from scrapy import http

class Spider(CrawlSpider):
    name = "share.anva.org.cn"
    allowed_domains = ["share.anva.org.cn"]
    start_urls = [
        # 'https://share.anva.org.cn/web/publicity/listPhishing',
        'https://share.anva.org.cn/web/publicity/listPhishing?type=phishing',
        'https://share.anva.org.cn/web/publicity/listMalware?type=malware',
        'https://share.anva.org.cn/web/publicity/listUrl?type=pm',

     ]
    def start_requests(self):
        for url in self.start_urls:
            list=[1,2,3,4,5]
            for i in list:
                if url.find('listPhishing') >= 0:
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-PHISHINGIP'},
                                           callback=self.parse_2)
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-PHISHINGURL'},
                                           callback=self.parse_1)
                elif url.find('listMalware') >= 0:
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-MMALWARE'},
                                           callback=self.parse_3)
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-PMALWARE'},
                                           callback=self.parse_3)
                elif url.find('listUrl') >= 0:
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-PMURL'},
                                           callback=self.parse_4)
                    yield http.FormRequest(url,formdata={'pageNow':str(i),'dataTypeCode':'ANVA-BL-PMIP'},
                                           callback=self.parse_5)

    # item数据格式规范
    @staticmethod
    def format_data(indicator,data_type,alive_time):
        tag = 8
        item = OpensourceThreatIntelItem()
        now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        item['indicator'] = indicator
        item['data_type'] = data_type
        item['tag'] = tag
        item['alive'] = True
        item['description'] = 'none'
        item['confidence'] = 5
        item['source'] = 'share.anva.org.cn'
        item['updated_time'] = alive_time
        item['created_time'] = now_time
        return item

    def parse_1(self, response):
        tag = 8
        sel = Selector(response)
        trs = sel.xpath('//*[@class="table table-bordered table-striped table-hover t_table"]/tr')
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[5])')[0].extract().strip()
            alive_time = content + 'T' + '00:00:00'
            url = tr.xpath('string(td[3])')[0].extract().strip()
            domain = tr.xpath('string(td[4])')[0].extract().strip()

            #url作为ID
            yield self.format_data(url,2,alive_time)
            #域名作为ID
            yield self.format_data(domain,1,alive_time)

    def parse_2(self, response):
        tag = 8
        sel = Selector(response)
        trs = sel.xpath('//*[@class="table table-bordered table-striped table-hover t_table"]/tr')
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[4])')[0].extract().strip()
            alive_time = content + 'T' + '00:00:00'
            ip = tr.xpath('string(td[3])')[0].extract().strip()

            #ip作为ID
            yield self.format_data(ip,0,alive_time)

    def parse_3(self, response):
        tag = 8
        sel = Selector(response)
        trs = sel.xpath('//*[@class="table table-bordered table-striped table-hover t_table"]/tr')
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[6])')[0].extract().strip()
            alive_time = content + 'T' + '00:00:00'
            md5 = tr.xpath('string(td[5])')[0].extract().strip()

            #md5作为ID
            yield self.format_data(md5,3,alive_time)

    def parse_4(self, response):
        tag = 8
        sel = Selector(response)
        trs = sel.xpath('//*[@class="table table-bordered table-striped table-hover t_table"]/tr')
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[5])')[0].extract().strip()
            alive_time = content + 'T' + '00:00:00'
            url = tr.xpath('string(td[3])')[0].extract().strip()
            md5 = tr.xpath('string(td[4])')[0].extract().strip()

            #url作为ID
            yield self.format_data(url,2,alive_time)
            #md5名作为ID
            yield self.format_data(md5,3,alive_time)

    def parse_5(self, response):
        tag = 8
        sel = Selector(response)
        trs = sel.xpath('//*[@class="table table-bordered table-striped table-hover t_table"]/tr')
        for i in range(1,len(trs)):
            tr = trs[i]
            content = tr.xpath('string(td[5])')[0].extract().strip()
            alive_time = content + 'T' + '00:00:00'
            ip = tr.xpath('string(td[3])')[0].extract().strip()
            md5 = tr.xpath('string(td[4])')[0].extract().strip()

            #ip作为ID
            yield self.format_data(ip,0,alive_time)
            #md5名作为ID
            yield self.format_data(md5,3,alive_time)




