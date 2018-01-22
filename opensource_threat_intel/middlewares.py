# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random

import requests
from fake_useragent import UserAgent  # 这是一个随机UserAgent的包，里面有很多UserAgent
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')  # 从setting文件中读取RANDOM_UA_TYPE值

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            """Gets random UA based on the type setting (random, firefox…)"""
            return getattr(self.ua, self.ua_type)

        user_agent_random = get_ua()
        request.headers.setdefault('User-Agent', user_agent_random)  # 这样就是实现了User-Agent的随即变换


class RandomProxyMiddleware(object):
    """动态设置ip代理"""

    def __init__(self):
        # self.url = "http://s.kxdaili.com/?api=201709051728283304&fitter=2&px=2"
        self.url = "http://10.24.45.79:38086/api/proxyAddr/"
        self.ips = []
        self.proxy_alive = []
        self.proxy_addr = ""
        self.proxy_size = 5
        self.test_url = "http://ip.chinaz.com/getip.aspx"
        if len(self.proxy_alive) < 2:
            self.update_proxy_pool()

    def update_proxy_pool(self):
        while len(self.proxy_alive) < self.proxy_size:
            if len(self.ips) < 1:
                logging.info("查询开心代理API,获取最新代理ip")
                # self.ips.extend(requests.get(self.url).content.split("\r\n"))
                self.ips.extend(requests.get(self.url).content.strip().split(";"))
            ip = random.choice(self.ips)
            self.ips.remove(ip)
            try:
                res = requests.get(self.test_url, timeout=2, proxies={"http": "http://" + ip})
                if res.status_code == 200:
                    logging.info("添加代理IP: %s,代理池长度: %s" % (ip, len(self.proxy_alive)))
                    self.proxy_alive.append("http://" + ip)
            except:
                pass

    def process_request(self, request, spider):
        if len(self.proxy_alive) < 2:
            logging.info("弹药不足,急需补充")
            self.update_proxy_pool()
        self.proxy_addr = random.choice(self.proxy_alive)
        print self.proxy_addr
        request.meta["proxy"] = self.proxy_addr  # request.meta["proxy"] = 'http://110.73.54.0:8123'

    def process_exception(self, request, exception, spider):
        try:
            self.proxy_alive.remove(self.proxy_addr)
            logging.error(u"删除失效代理IP %s ,代理池长度: %s ,请求 %s 异常: %s" % (
                self.proxy_addr, len(self.proxy_alive), request.url, exception))
        except:
            logging.error(u"meta代理不成功,代理池长度: %s ,请求 %s 异常: %s" % (len(self.proxy_alive), request.url, exception))
            pass


class PhantomJSMiddleware(object):
    # overwrite process request

    def __init__(self):
        pass

    def process_request(self, request, spider):
        PHANTOMJS_ARGS = [
            # "--proxy=<proxy address>:<proxy port>",
            # "--proxy-type=http,https",
            "--load-images=false",
            "--ignore-ssl-errors=true",
            "--ssl-protocol=any"
        ]
        if request.meta.has_key('PhantomJS'):
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            # dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
            # dcap["phantomjs.page.settings.webSecurityEnabled"] = False
            # dcap["phantomjs.page.settings.javascriptCanOpenWindows"] = False
            # dcap["phantomjs.page.settings.javascriptCanCloseWindows"] = False
            # dcap = {'acceptSslCerts':True}
            dcap["phantomjs.page.customHeaders"] = request.headers
            dcap["takesScreenshot"] = False
            service_args = list(PHANTOMJS_ARGS)
            driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args = service_args)
            # driver.implicitly_wait(30)
            driver.add_cookie(request.meta['cookie'])
            driver.get(request.url)
            js = "window.scrollTo(0, document.body.scrollHeight)"
            driver.execute_script(js)
            try:
                wait = WebDriverWait(driver, 2)
                element = wait.until(EC.element_to_be_clickable((By.ID, 'someid')))
            except:
                pass
            content = driver.page_source.encode('utf-8')
            url = driver.current_url.encode('utf-8')
            driver.quit()
            return HtmlResponse(url, encoding = 'utf-8', status = 200, body = content)
