#!/usr/bin/python3
# coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup
import codecs
import traceback
import time
import random

# 回传cookie
class RequestsBrowser:

    def __init__(self, headers=None, cookies=None):
        self.cookies = cookies
        self.headers = headers
        self.last_cookies = cookies
        self.last_status = None
        self.last_html = None
        self.response_headers = None
        self.url = None
        self.encoding = 'UTF-8'

    def get(self, _url, headers=None, cookies=None, encoding=None):
        if not cookies:
            cookies = self.cookies

        if not encoding:
            encoding = self.encoding

        if not headers:
            headers = self.headers
        self.url = _url
        html = requests.get(self.url, headers=headers, cookies=cookies)
        html.encoding = encoding
        self.last_status = html.status_code
        self.last_html = html.text
        self.response_headers = html.headers
        self.last_cookies = html.cookies
        self.url = _url
        return self.last_html

    def get_soup(self,  _url, headers=None, cookies=None, encoding=None):
        self.get(_url, headers=headers, cookies=cookies, encoding=encoding)
        return BeautifulSoup(self.last_html, 'html.parser')


class Biquget:

    def __init__(self, book_name, start_url):

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
        self.encoding = "GBK"
        self.next_url = start_url
        self.book_name = book_name
        self.file_name = book_name + ".txt"
        self.f = None
        self.finish = False
        self.browser = RequestsBrowser(headers=headers)

    # 支持 with，进入时调用
    def __enter__(self):
        self.f = codecs.open(self.file_name, 'ab', encoding='utf-8')
        return self

    # 支持with 退出时调用
    def __exit__(self, exc_type, exc_value, tb):
        if self.f and not self.f.closed:
            self.f.close()

        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            print(self.next_url)
            # return False # uncomment to pass exception through
        return True

    def close(self):
        self.__exit__()

    def next(self):
        soup = self.browser.get_soup(self.next_url, encoding=self.encoding)
        title = soup.find('div', attrs={'class': 'bookname'}).find('h1').getText()
        content = soup.find('div', attrs={'id': 'content'}).getText()

        # links_div = soup.find('div', attrs={"class":"bottem1"})
        # if links_div :
        #     links = links_div.find_all("a")
        #     if len(links) == 5:
        #         links[]

        next_url = soup.find(name='a', text="下一章").get('href')
        # 下面这个链接找不到
        contents_table_url = soup.find(name='a', text="章节目录").get('href')

        if next_url != contents_table_url:
            self.next_url = next_url
        else:
            self.finish = True
        return title, content

    def __iter__(self):
        return self

    def __next__(self):
        if not self.finish:
            title, content = self.next()
            self.f.write(u'{title}\n{content}'.format(title=title, content=content))
        else:
            print("全书完成")
            raise StopIteration()

#大数据修仙
if __name__ == '__main__':
    # start_url = 'https://www.biquge5200.com/83_83419/170271447.html'  # 第一章节网站
    print(sys.argv)
    start_url = sys.argv[1]
    # book_name = "大数据修仙"
    book_name = sys.argv[2]
    with Biquget(book_name, start_url) as biquge:
        print(biquge)
        try:
            # 枚举+索引
            for i, mn in enumerate(biquge):
                print(i,biquge.next_url)
                if i % 50 == 0:
                    #每隔50次访问休眠2分钟
                    time.sleep(120)
                else:
                    #每次抓取休眠0.1秒
                    time.sleep(0.2)

        except requests.exceptions.ConnectionError as e:
            print(e, biquge.next_url)
        #except requests.exceptions.ConnectionError as e:

        #怎么恢复
        #time.sleep(600)
