import urllib
import requests
import time
import random
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

page_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Host': 'www.zhipin.com',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.zhipin.com/',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'lastCity=101010100; __c=1560175643; __g=-; JSESSIONID=5CEE199DE881108BD5A8D4335B72974B; t=GhIYKPBA1hVAPL3s; wt=GhIYKPBA1hVAPL3s; __l=l=%2Fwww.zhipin.com%2F&r=; __a=18622455.1560175643..1560175643.5.1.5.5; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1560175643; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1560175780'
}

# 设置搜索职位名称
key_words = "数据分析"
key = urllib.parse.quote(key_words)


# url='https://www.zhipin.com/c101010100/?query='+key+'&page=1&ka=page-1'

def get_data(url):
    try:
        res = requests.get(url, headers=page_headers)
        status = res.status_code
        data = res.text
        print(status)
        soup = BeautifulSoup(data, 'lxml')
        print(res.text)
        # print(soup.prettify())  #输出格式化的html代码
        return soup, status

    except Exception as e:
        print(str(e))
        return 0, 0


def get_job(url):
    soup, status = get_data(url)
    if status == 200:
        job_all = soup.find_all('div', class_="job-primary")
        for job in job_all:
            try:
                # 职位名
                job_title = job.find('div', class_="job-title").string
                # 薪资
                job_salary = job.find('span', class_="red").string
                # 职位标签
                job_tag1 = job.p.text
                # 公司
                job_company = job.find('div', class_="company-text").a.text
                # 招聘详情页链接
                job_url = job.find('div', class_="company-text").a.attrs['href']
                # 公司标签
                job_tag2 = job.find('div', class_="company-text").p.text
                # 发布时间
                job_time = job.find('div', class_="info-publis").p.text

                with open('job.csv', 'a+', encoding='utf-8') as fh:
                    fh.write(
                        job_company + "," + job_title + "," + job_salary + "," + job_tag1 + "," + job_time + "," + job_tag2 + ",https://www.zhipin.com" + job_url + "\n")
            except Exception as e:
                print(str(e))


if __name__ == '__main__':
    with open('job.csv', 'w', encoding='utf-8') as fh:
        fh.write("公司,职位名,薪资,职位标签,发布时间,公司标签,招聘链接\n")
    for i in range(1, 11):
        print("正在爬取第 %s 页..." % i)
        url = 'https://www.zhipin.com/c101010100/?query=' + key + '&page=' + str(i) + '&ka=page-' + str(i)
        get_job(url)
        # 随机等待
        span = round(random.random() * 6, 1)
        time.sleep(span)
