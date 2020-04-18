# project:  seleniumChromedriver
# author:  liulei
# time:  2019/8/8 11:29
# file:  bossSpider.py
import random
import time
from lxml import etree
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BossSpider(object):
    #driver_path = r'C:\chromedriver\chromedriver.exe'

    def __init__(self):
        #self.driver = webdriver.Chrome(executable_path=BossSpider.driver_path)
        self.driver = webdriver.Chrome()

        self.url = 'https://www.zhipin.com/job_detail/?query=python&city=101010100&industry=&position='
        self.domain = 'https://www.zhipin.com'
        fp = open('boss.csv', 'a', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(fp,
                                     ['position_name', 'company', 'salary', 'city', 'salary', 'work_years', 'education',
                                      'job_desc'])
        self.writer.writeheader()

    def run(self):
        self.driver.get(self.url)
        page_num = 1
        while True:
            source = self.driver.page_source
            self.parse_list_page(source, page_num)
            WebDriverWait(driver=self.driver, timeout=1000).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='page']/a[@class='next']"))

            )

            next_btn = self.driver.find_element_by_xpath("//div[@class='page']/a[@class='next']")
            time.sleep(random.randint(1, 3))

            if next_btn.get_attribute('class') != 'next':
                print("已经是最后一页了,爬取完成……")
                break
            else:
                next_btn.click()
                page_num += 1

    def parse_list_page(self, source, page_num):
        html = etree.HTML(source)
        links = html.xpath("//div[@class ='info-primary']//h3[@class ='name']/a/@href")
        postion_num = 1
        for link in links:
            link = self.domain + link
            print("正在解析第%s页 第%s条数据" % (page_num, postion_num))
            self.driver.execute_script("window.scrollTo(0,3000)")
            self.request_detail_page(link)
            postion_num += 1
            time.sleep(random.randint(1, 3))

    def request_detail_page(self, url):
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, timeout=300).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='info-primary']//div[@class='name']"))
        )
        source = self.driver.page_source
        self.parse_detail_page(source)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self, source):
        html = etree.HTML(source)
        position_name = html.xpath("//div[@class='info-primary']//div[@class='name']/h1/text()")[0].strip()
        salary = html.xpath("//div[@class='name']//span/text()")[0]
        city = html.xpath("//div[@class='info-primary']/p/text()")[0]
        work_years = html.xpath("//div[@class='info-primary']/p/text()")[1]
        education = html.xpath("//div[@class='info-primary']/p/text()")[2]
        company = html.xpath("//a[@ka='job-detail-company_custompage']//text()")[0].strip()
        job_desc = " ".join(html.xpath("//div[@class='job-sec']/div[@class='text']//text()")).strip()
        position = {
            'position_name': position_name,
            'company': company,
            'salary': salary,
            'city': city,
            'work_years': work_years,
            'education': education,
            'job_desc': job_desc
        }
        self.writer_position(position)
        print(position)
        print('*' * 50)

    def writer_position(self, position):
        self.writer.writerow(position)


def main():
    bossSpider = BossSpider()
    bossSpider.run()


if __name__ == '__main__':
    main()
