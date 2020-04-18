# -*- coding:utf-8 -*-
import re,requests
from lxml import etree
import logging,time,random, json
from bs4 import BeautifulSoup
from splinter import Browser
from selenium.webdriver.chrome.options import Options


'''保存日志方便查看'''
logging.basicConfig(filename='logging.log',
                    format='%(asctime)s %(message)s',
                    filemode="w", level=logging.DEBUG)

zhilian_city_codes = {
        "name": "天津",
        "en_name": "TIANJIN",
        "code": "531",
        "sublist": [
            {
                "name": "宝坻区",
                "en_name": "Baodi",
                "code": "2177",
                "sublist": []
            },
            {
                "name": "北辰区",
                "en_name": "Beichen",
                "code": "2175",
                "sublist": []
            },
            {
                "name": "滨海新区",
                "en_name": "Binhaixin",
                "code": "2171",
                "sublist": []
            },
            {
                "name": "东丽区",
                "en_name": "Dongli",
                "code": "2172",
                "sublist": []
            },
            {
                "name": "河北区",
                "en_name": "Hebei",
                "code": "2169",
                "sublist": []
            },
            {
                "name": "河东区",
                "en_name": "Hedong",
                "code": "2166",
                "sublist": []
            },
            {
                "name": "和平区",
                "en_name": "Heping",
                "code": "2165",
                "sublist": []
            },
            {
                "name": "河西区",
                "en_name": "Hexi",
                "code": "2167",
                "sublist": []
            },
            {
                "name": "红桥区",
                "en_name": "Hongqiao",
                "code": "2170",
                "sublist": []
            },
            {
                "name": "静海区",
                "en_name": "Jinghai",
                "code": "2178",
                "sublist": []
            },
            {
                "name": "津南区",
                "en_name": "Jinnan",
                "code": "2174",
                "sublist": []
            },
            {
                "name": "蓟州区",
                "en_name": "Ji",
                "code": "2180",
                "sublist": []
            },
            {
                "name": "南开区",
                "en_name": "Nankai",
                "code": "2168",
                "sublist": []
            },
            {
                "name": "宁河区",
                "en_name": "Ninghe",
                "code": "2179",
                "sublist": []
            },
            {
                "name": "武清区",
                "en_name": "Wuqing",
                "code": "2176",
                "sublist": []
            },
            {
                "name": "西青区",
                "en_name": "Xiqing",
                "code": "2173",
                "sublist": []
            }
        ]
    }

# 回传cookie

'''
from selenium import webdriver
# 谷歌浏览启动配置
option = webdriver.ChromeOptions()
# 配置参数 禁止 Chrome 正在受到自动化软件控制
option.add_argument('disable-infobars')

'''


# 智联招聘 职位扫描
class ZhaopinSpider:

    def __init__(self,  city_names = ('天津',) , job_names = ('大数据',), headless=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cookie': 'GeeTestUser=393f6749747633d849ccfed29dd6853a; GeeTestAjaxUser=e0a9e16cf285f0b0e4bb2be9a58e36e2',
            'Host': 'www.zhaopin.com',
            'Referer': 'https://www.zhaopin.com/',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        self.browser = None
        self.headless = headless
        self.html = None
        self.city_names = city_names
        self.job_names = job_names
        self.city_urls = None
        self.area_urls = None
        self.city_urls_template = "https://sou.zhaopin.com/?jl={city_code}&kw={keyword}&kt=3"

    def __enter__(self):
        #executable_path = {'executable_path':'C:\\Program Files\\Firefox\\firefox.exe'}
        chrome_options = Options()
        #chrome_options.add_argument('disable-infobars')
        #chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        #self.browser = Browser("firefox", headless=self.headless, options=chrome_options)
        self.browser = Browser("firefox", headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.browser:
            self.browser.quit()

    def visit(self, url):
        self.browser.visit(url)
        tag = self.browser.find_by_text('行政区')

        self.html = self.browser.html

        return BeautifulSoup(self.html, 'html.parser')

    def gen_city_url(self):
        self.city_urls = []
        for kw in self.job_names:
            for city in self.city_names:
                city_code = zhilian_city_codes.get(city)
                _url = self.city_urls_template.format(city_code=city_code, keyword=kw)
                self.city_urls.append((kw, _url))
        return self.city_urls
    '''
        def gen_area_url(self, url):
        self.browser.visit(url)
        tag = self.browser.find_by_id("queryTitleUls")
        tags = tag.find_by_css('.local-type__text')
        tags.first.click()
        for link_tag in area_links:
            print(link_tag)
    '''


if __name__ == '__main__':

    with ZhaopinSpider(headless=False) as spider:
        spider.gen_city_url()
        for url in spider.city_urls:
            spider.gen_area_url(url[1])
        print(spider.city_urls)