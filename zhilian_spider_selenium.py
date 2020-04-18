# -*- coding:utf-8 -*-
import re,requests
from lxml import etree
import logging,time,random, json
from bs4 import BeautifulSoup
# from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#from selenium.webdriver.chrome.options import Options
'''
splinter 有一个意外的异常
  File "/Users/laofeng/PycharmProjects/disk_search/venv/lib/python3.7/site-packages/splinter/browser.py", line 68, in get_driver
    raise e
UnboundLocalError: local variable 'e' referenced before assignment

在这个文件中直接使用 selenium
'''

'''保存日志方便查看'''
logging.basicConfig(filename='logging.log',
                    format='%(asctime)s %(message)s',
                    filemode="w", level=logging.DEBUG)

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler=logging.FileHandler("log.txt")
handler.setLevel(logging.DEBUG)
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console=logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(console)

hot_citys =  {'全国': {'en_name': 'ALL', 'code': '489', 'name': '全国', 'sublist': []}, '北京': {'en_name': 'BEIJING', 'code': '530', 'name': '北京', 'sublist': [{'en_name': 'BEIJING', 'code': '530', 'name': '北京', 'sublist': []}, {'en_name': 'Dongcheng', 'code': '2001', 'name': '东城区', 'sublist': []}, {'en_name': 'Xicheng', 'code': '2002', 'name': '西城区', 'sublist': []}, {'en_name': 'Chongwen', 'code': '2003', 'name': '崇文区', 'sublist': []}, {'en_name': 'Xuanwu', 'code': '2004', 'name': '宣武区', 'sublist': []}, {'en_name': 'Haidian', 'code': '2005', 'name': '海淀区', 'sublist': []}, {'en_name': 'Chaoyang', 'code': '2006', 'name': '朝阳区', 'sublist': []}, {'en_name': 'Fengtai', 'code': '2007', 'name': '丰台区', 'sublist': []}, {'en_name': 'Shijingshan', 'code': '2008', 'name': '石景山区', 'sublist': []}, {'en_name': 'Tongzhou', 'code': '2009', 'name': '通州区', 'sublist': []}, {'en_name': 'Shunyi', 'code': '2010', 'name': '顺义区', 'sublist': []}, {'en_name': 'Fangshan', 'code': '2011', 'name': '房山区', 'sublist': []}, {'en_name': 'Daxing', 'code': '2012', 'name': '大兴区', 'sublist': []}, {'en_name': 'Changping', 'code': '2013', 'name': '昌平区', 'sublist': []}, {'en_name': 'Huairou', 'code': '2014', 'name': '怀柔区', 'sublist': []}, {'en_name': 'Pinggu', 'code': '2015', 'name': '平谷区', 'sublist': []}, {'en_name': 'Mentougou', 'code': '2016', 'name': '门头沟区', 'sublist': []}, {'en_name': 'Miyun', 'code': '2017', 'name': '密云县', 'sublist': []}, {'en_name': 'Yanqing', 'code': '2018', 'name': '延庆县', 'sublist': []}]}, '上海': {'en_name': 'SHANGHAI', 'code': '538', 'name': '上海', 'sublist': [{'en_name': 'SHANGHAI', 'code': '538', 'name': '上海', 'sublist': []}, {'en_name': 'Huangpu', 'code': '2019', 'name': '黄浦区', 'sublist': []}, {'en_name': 'Xuhui', 'code': '2021', 'name': '徐汇区', 'sublist': []}, {'en_name': 'Changning', 'code': '2022', 'name': '长宁区', 'sublist': []}, {'en_name': 'Jingan', 'code': '2023', 'name': '静安区', 'sublist': []}, {'en_name': 'Putuo', 'code': '2024', 'name': '普陀区', 'sublist': []}, {'en_name': 'Zhabei', 'code': '2025', 'name': '闸北区', 'sublist': []}, {'en_name': 'Hongkou', 'code': '2026', 'name': '虹口区', 'sublist': []}, {'en_name': 'Yangpu', 'code': '2027', 'name': '杨浦区', 'sublist': []}, {'en_name': 'Minxing', 'code': '2028', 'name': '闵行区', 'sublist': []}, {'en_name': 'Baoshan', 'code': '2029', 'name': '宝山区', 'sublist': []}, {'en_name': 'Jiading', 'code': '2030', 'name': '嘉定区', 'sublist': []}, {'en_name': 'Pudongxin', 'code': '2031', 'name': '浦东新区', 'sublist': []}, {'en_name': 'Jinshan', 'code': '2032', 'name': '金山区', 'sublist': []}, {'en_name': 'Songjiang', 'code': '2033', 'name': '松江区', 'sublist': []}, {'en_name': 'Qingpu', 'code': '2034', 'name': '青浦区', 'sublist': []}, {'en_name': 'Fengxian', 'code': '2035', 'name': '奉贤区', 'sublist': []}, {'en_name': 'Chongming', 'code': '2036', 'name': '崇明县', 'sublist': []}]}, '深圳': {'en_name': 'SHENZHEN', 'code': '765', 'name': '深圳', 'sublist': [{'en_name': 'SHENZHEN', 'code': '765', 'name': '深圳', 'sublist': []}, {'en_name': 'Futian', 'code': '2037', 'name': '福田区', 'sublist': []}, {'en_name': 'Luohu', 'code': '2038', 'name': '罗湖区', 'sublist': []}, {'en_name': 'Nanshan', 'code': '2039', 'name': '南山区', 'sublist': []}, {'en_name': 'Yantian', 'code': '2040', 'name': '盐田区', 'sublist': []}, {'en_name': 'Baoan', 'code': '2041', 'name': '宝安区', 'sublist': []}, {'en_name': 'Longgang', 'code': '2042', 'name': '龙岗区', 'sublist': []}, {'en_name': 'Pingshanxin', 'code': '2043', 'name': '坪山新区', 'sublist': []}, {'en_name': 'Guangmingxin', 'code': '2044', 'name': '光明新区', 'sublist': []}, {'en_name': 'Longhua', 'code': '2361', 'name': '龙华新区', 'sublist': []}, {'en_name': 'Dapeng', 'code': '2362', 'name': '大鹏新区', 'sublist': []}]}, '广州': {'en_name': 'GUANGZHOU', 'code': '763', 'name': '广州', 'sublist': [{'en_name': 'GUANGZHOU', 'code': '763', 'name': '广州', 'sublist': []}, {'en_name': 'Yuexiu', 'code': '2045', 'name': '越秀区', 'sublist': []}, {'en_name': 'Haizhu', 'code': '2046', 'name': '海珠区', 'sublist': []}, {'en_name': 'Liwan', 'code': '2047', 'name': '荔湾区', 'sublist': []}, {'en_name': 'Tianhe', 'code': '2048', 'name': '天河区', 'sublist': []}, {'en_name': 'Baiyun', 'code': '2049', 'name': '白云区', 'sublist': []}, {'en_name': 'Huangpu', 'code': '2050', 'name': '黄埔区', 'sublist': []}, {'en_name': 'Fanyu', 'code': '2052', 'name': '番禺区', 'sublist': []}, {'en_name': 'Huadu', 'code': '2051', 'name': '花都区', 'sublist': []}, {'en_name': 'Luogang', 'code': '2053', 'name': '萝岗区', 'sublist': []}, {'en_name': 'Nansha', 'code': '2054', 'name': '南沙区', 'sublist': []}, {'en_name': 'ZENGCHENG', 'code': '2475', 'name': '增城', 'sublist': []}, {'en_name': 'CONGHUA', 'code': '2474', 'name': '从化', 'sublist': []}]}, '天津': {'en_name': 'TIANJIN', 'code': '531', 'name': '天津', 'sublist': [{'en_name': 'TIANJIN', 'code': '531', 'name': '天津', 'sublist': []}, {'en_name': 'Heping', 'code': '2165', 'name': '和平区', 'sublist': []}, {'en_name': 'Hedong', 'code': '2166', 'name': '河东区', 'sublist': []}, {'en_name': 'Hexi', 'code': '2167', 'name': '河西区', 'sublist': []}, {'en_name': 'Nankai', 'code': '2168', 'name': '南开区', 'sublist': []}, {'en_name': 'Hebei', 'code': '2169', 'name': '河北区', 'sublist': []}, {'en_name': 'Hongqiao', 'code': '2170', 'name': '红桥区', 'sublist': []}, {'en_name': 'Binhaixin', 'code': '2171', 'name': '滨海新区', 'sublist': []}, {'en_name': 'Dongli', 'code': '2172', 'name': '东丽区', 'sublist': []}, {'en_name': 'Xiqing', 'code': '2173', 'name': '西青区', 'sublist': []}, {'en_name': 'Jinnan', 'code': '2174', 'name': '津南区', 'sublist': []}, {'en_name': 'Beichen', 'code': '2175', 'name': '北辰区', 'sublist': []}, {'en_name': 'Wuqing', 'code': '2176', 'name': '武清区', 'sublist': []}, {'en_name': 'Baodi', 'code': '2177', 'name': '宝坻区', 'sublist': []}, {'en_name': 'Jinghai', 'code': '2178', 'name': '静海县', 'sublist': []}, {'en_name': 'Ninghe', 'code': '2179', 'name': '宁河县', 'sublist': []}, {'en_name': 'Ji', 'code': '2180', 'name': '蓟县', 'sublist': []}]}, '成都': {'en_name': 'CHENGDU', 'code': '801', 'name': '成都', 'sublist': [{'en_name': 'CHENGDU', 'code': '801', 'name': '成都', 'sublist': []}, {'en_name': 'Qingyang', 'code': '2107', 'name': '青羊区', 'sublist': []}, {'en_name': 'Jinjiang', 'code': '2108', 'name': '锦江区', 'sublist': []}, {'en_name': 'Jinniu', 'code': '2109', 'name': '金牛区', 'sublist': []}, {'en_name': 'Wuhou', 'code': '2110', 'name': '武侯区', 'sublist': []}, {'en_name': 'Chenghua', 'code': '2111', 'name': '成华区', 'sublist': []}, {'en_name': 'Longquanyi', 'code': '2112', 'name': '龙泉驿区', 'sublist': []}, {'en_name': 'Qingbaijiang', 'code': '2113', 'name': '青白江区', 'sublist': []}, {'en_name': 'Xindu', 'code': '2114', 'name': '新都区', 'sublist': []}, {'en_name': 'Wenjiang', 'code': '2115', 'name': '温江区', 'sublist': []}, {'en_name': 'Shuangliu', 'code': '2116', 'name': '双流县', 'sublist': []}, {'en_name': 'pi', 'code': '2117', 'name': '郫县', 'sublist': []}, {'en_name': 'Jintang', 'code': '2118', 'name': '金堂县', 'sublist': []}, {'en_name': 'Dayi', 'code': '2119', 'name': '大邑县', 'sublist': []}, {'en_name': 'Pujiang', 'code': '2120', 'name': '蒲江县', 'sublist': []}, {'en_name': 'Xinjin', 'code': '2121', 'name': '新津县', 'sublist': []}, {'en_name': 'Qionglai', 'code': '2377', 'name': '邛崃市', 'sublist': []}, {'en_name': 'Chongzhou', 'code': '2378', 'name': '崇州市', 'sublist': []}, {'en_name': 'Pengzhou', 'code': '2379', 'name': '彭州市', 'sublist': []}, {'en_name': 'Dujiangyan', 'code': '2380', 'name': '都江堰市', 'sublist': []}, {'en_name': 'Gaoxinqu', 'code': '2381', 'name': '高新区', 'sublist': []}]}, '杭州': {'en_name': 'HANGZHOU', 'code': '653', 'name': '杭州', 'sublist': [{'en_name': 'HANGZHOU', 'code': '653', 'name': '杭州', 'sublist': []}, {'en_name': 'Binjiang', 'code': '2238', 'name': '滨江区', 'sublist': []}, {'en_name': 'Chunan', 'code': '2242', 'name': '淳安县', 'sublist': []}, {'en_name': 'FUYANG', 'code': '2478', 'name': '富阳市', 'sublist': []}, {'en_name': 'Gongshu', 'code': '2236', 'name': '拱墅区', 'sublist': []}, {'en_name': 'Jiande', 'code': '2409', 'name': '建德市', 'sublist': []}, {'en_name': 'Jianggan', 'code': '2235', 'name': '江干区', 'sublist': []}, {'en_name': 'LINAN', 'code': '2479', 'name': '临安市', 'sublist': []}, {'en_name': 'Shangcheng', 'code': '2233', 'name': '上城区', 'sublist': []}, {'en_name': 'Tonglu', 'code': '2241', 'name': '桐庐县', 'sublist': []}, {'en_name': 'Xiacheng', 'code': '2234', 'name': '下城区', 'sublist': []}, {'en_name': 'Xiaoshan', 'code': '2239', 'name': '萧山区', 'sublist': []}, {'en_name': 'Xiasha', 'code': '2457', 'name': '下沙', 'sublist': []}, {'en_name': 'Xihu', 'code': '2237', 'name': '西湖区', 'sublist': []}, {'en_name': 'Yuhang', 'code': '2240', 'name': '余杭区', 'sublist': []}]}, '武汉': {'en_name': 'WUHAN', 'code': '736', 'name': '武汉', 'sublist': [{'en_name': 'WUHAN', 'code': '736', 'name': '武汉', 'sublist': []}, {'en_name': 'Caidian', 'code': '2064', 'name': '蔡甸区', 'sublist': []}, {'en_name': 'Changkou', 'code': '2059', 'name': '硚口区', 'sublist': []}, {'en_name': 'Donghuxinqu', 'code': '2366', 'name': '东湖新技术开发区', 'sublist': []}, {'en_name': 'Dongxihu', 'code': '2065', 'name': '东西湖区', 'sublist': []}, {'en_name': 'Hannan', 'code': '2066', 'name': '汉南区', 'sublist': []}, {'en_name': 'Hanyang', 'code': '2060', 'name': '汉阳区', 'sublist': []}, {'en_name': 'Hongshan', 'code': '2063', 'name': '洪山区', 'sublist': []}, {'en_name': 'Huangpo', 'code': '2068', 'name': '黄陂区', 'sublist': []}, {'en_name': 'Jiangan', 'code': '2057', 'name': '江岸区', 'sublist': []}, {'en_name': 'Jianghan', 'code': '2058', 'name': '江汉区', 'sublist': []}, {'en_name': 'Jiangxia', 'code': '2067', 'name': '江夏区', 'sublist': []}, {'en_name': 'Jingjikaifaqu', 'code': '2365', 'name': '武汉经济技术开发区', 'sublist': []}, {'en_name': 'Qingshan', 'code': '2062', 'name': '青山区', 'sublist': []}, {'en_name': 'Wuchang', 'code': '2061', 'name': '武昌区', 'sublist': []}, {'en_name': 'Wujiashan', 'code': '2367', 'name': '武汉吴家山经济技术开发区', 'sublist': []}, {'en_name': 'Xinzhou', 'code': '2069', 'name': '新洲区', 'sublist': []}]}, '大连': {'en_name': 'DALIAN', 'code': '600', 'name': '大连', 'sublist': [{'en_name': 'DALIAN', 'code': '600', 'name': '大连', 'sublist': []}, {'en_name': 'Changhai', 'code': '2397', 'name': '长海县', 'sublist': []}, {'en_name': 'Changxing', 'code': '2398', 'name': '长兴岛', 'sublist': []}, {'en_name': 'Ganjingzi', 'code': '2184', 'name': '甘井子区', 'sublist': []}, {'en_name': 'Gaoxinyuanqu', 'code': '2185', 'name': '高新园区', 'sublist': []}, {'en_name': 'Jinzhou', 'code': '2188', 'name': '金州区 ', 'sublist': []}, {'en_name': 'Kaifaqu', 'code': '2186', 'name': '开发区', 'sublist': []}, {'en_name': 'Lvshunkou', 'code': '2187', 'name': '旅顺口区', 'sublist': []}, {'en_name': 'Pulandian', 'code': '2394', 'name': '普兰店市', 'sublist': []}, {'en_name': 'Shahekou', 'code': '2183', 'name': '沙河口区', 'sublist': []}, {'en_name': 'Wafangdian', 'code': '2395', 'name': '瓦房店市', 'sublist': []}, {'en_name': 'Xigang', 'code': '2181', 'name': '西岗区', 'sublist': []}, {'en_name': 'Zhongshan', 'code': '2182', 'name': '中山区', 'sublist': []}, {'en_name': 'Zhuanghe', 'code': '2396', 'name': '庄河市', 'sublist': []}]}, '长春': {'en_name': 'CHANGCHUN', 'code': '613', 'name': '长春', 'sublist': [{'en_name': 'CHANGCHUN', 'code': '613', 'name': '长春', 'sublist': []}, {'en_name': 'Chaoyang', 'code': '2142', 'name': '朝阳区', 'sublist': []}, {'en_name': 'Dehui', 'code': '2389', 'name': '德惠市', 'sublist': []}, {'en_name': 'Erdao', 'code': '2143', 'name': '二道区', 'sublist': []}, {'en_name': 'Gaoxinkaifaqu', 'code': '2145', 'name': '高新开发区', 'sublist': []}, {'en_name': 'Jingjikaifaqu', 'code': '2146', 'name': '经济开发区', 'sublist': []}, {'en_name': 'Jiutai', 'code': '2388', 'name': '九台市', 'sublist': []}, {'en_name': 'Kuancheng', 'code': '2141', 'name': '宽城区', 'sublist': []}, {'en_name': 'Lvyuan', 'code': '2144', 'name': '绿园区', 'sublist': []}, {'en_name': 'Nanguan', 'code': '2140', 'name': '南关区', 'sublist': []}, {'en_name': 'Nongan', 'code': '2390', 'name': '农安县', 'sublist': []}, {'en_name': 'Qichechanyekaifaqu', 'code': '2147', 'name': '汽车产业开发区', 'sublist': []}, {'en_name': 'Shuangyang', 'code': '2148', 'name': '双阳区', 'sublist': []}, {'en_name': 'Yushu', 'code': '2387', 'name': '榆树市', 'sublist': []}]}, '南京': {'en_name': 'NANJING', 'code': '635', 'name': '南京', 'sublist': [{'en_name': 'NANJING', 'code': '635', 'name': '南京', 'sublist': []}, {'en_name': 'Xuanwu', 'code': '2084', 'name': '玄武区', 'sublist': []}, {'en_name': 'Qinhuai', 'code': '2086', 'name': '秦淮区', 'sublist': []}, {'en_name': 'JianYe', 'code': '2087', 'name': '建邺区', 'sublist': []}, {'en_name': 'Gulou', 'code': '2088', 'name': '鼓楼区', 'sublist': []}, {'en_name': 'Pukou', 'code': '2090', 'name': '浦口区', 'sublist': []}, {'en_name': 'Liuhe', 'code': '2091', 'name': '六合区', 'sublist': []}, {'en_name': 'Qixia', 'code': '2092', 'name': '栖霞区', 'sublist': []}, {'en_name': 'Yuhuatai', 'code': '2093', 'name': '雨花台区', 'sublist': []}, {'en_name': 'Jiangning', 'code': '2094', 'name': '江宁区', 'sublist': []}, {'en_name': 'Lishui', 'code': '2095', 'name': '溧水县', 'sublist': []}, {'en_name': 'Gaochun', 'code': '2096', 'name': '高淳县', 'sublist': []}]}, '济南': {'en_name': 'JINAN', 'code': '702', 'name': '济南', 'sublist': [{'en_name': 'JINAN', 'code': '702', 'name': '济南', 'sublist': []}, {'en_name': 'Changqing', 'code': '2102', 'name': '长清区', 'sublist': []}, {'en_name': 'Gaoxinqu', 'code': '2376', 'name': '高新区', 'sublist': []}, {'en_name': 'Huaiyin', 'code': '2100', 'name': '槐荫区', 'sublist': []}, {'en_name': 'Jiyang', 'code': '2104', 'name': '济阳县', 'sublist': []}, {'en_name': 'Licheng', 'code': '2101', 'name': '历城区', 'sublist': []}, {'en_name': 'Lixia', 'code': '2098', 'name': '历下区', 'sublist': []}, {'en_name': 'Pingyin', 'code': '2103', 'name': '平阴县', 'sublist': []}, {'en_name': 'Shanghe', 'code': '2105', 'name': '商河县', 'sublist': []}, {'en_name': 'Shizhong', 'code': '2097', 'name': '市中区', 'sublist': []}, {'en_name': 'Tianqiao', 'code': '2099', 'name': '天桥区', 'sublist': []}, {'en_name': 'Zhangqiu', 'code': '2471', 'name': '章丘市', 'sublist': []}]}, '青岛': {'en_name': 'QINGDAO', 'code': '703', 'name': '青岛', 'sublist': [{'en_name': 'QINGDAO', 'code': '703', 'name': '青岛', 'sublist': []}, {'en_name': 'Baoshuiqu', 'code': '2391', 'name': '保税区', 'sublist': []}, {'en_name': 'Chanyekaifaqu', 'code': '2393', 'name': '青岛高新技术产业开发区', 'sublist': []}, {'en_name': 'Chengyang', 'code': '2159', 'name': '城阳区', 'sublist': []}, {'en_name': 'Huangdao', 'code': '2157', 'name': '黄岛区（新行政区）', 'sublist': []}, {'en_name': 'Jiaozhoushi', 'code': '2160', 'name': '胶州市', 'sublist': []}, {'en_name': 'Jimoshi', 'code': '2161', 'name': '即墨市', 'sublist': []}, {'en_name': 'Jingjikaifaqu', 'code': '2392', 'name': '青岛经济技术开发区', 'sublist': []}, {'en_name': 'Laixishi', 'code': '2164', 'name': '莱西市', 'sublist': []}, {'en_name': 'Laoshan', 'code': '2158', 'name': '崂山区', 'sublist': []}, {'en_name': 'Licang', 'code': '2156', 'name': '李沧区', 'sublist': []}, {'en_name': 'Pingdushi', 'code': '2162', 'name': '平度市', 'sublist': []}, {'en_name': 'Shibei', 'code': '2154', 'name': '市北区（新行政区）', 'sublist': []}, {'en_name': 'Shinan', 'code': '2153', 'name': '市南区', 'sublist': []}]}, '苏州': {'en_name': 'SUZHOU', 'code': '639', 'name': '苏州', 'sublist': [{'en_name': 'SUZHOU', 'code': '639', 'name': '苏州', 'sublist': []}, {'en_name': 'Gaoxinqu', 'code': '2404', 'name': '高新区', 'sublist': []}, {'en_name': 'Gongyeyuang', 'code': '2218', 'name': '工业园区', 'sublist': []}, {'en_name': 'GUSUQU', 'code': '2511', 'name': '姑苏区', 'sublist': []}, {'en_name': 'Huqiu', 'code': '2215', 'name': '虎丘区', 'sublist': []}, {'en_name': 'WUJIANGQU', 'code': '2561', 'name': '吴江区', 'sublist': []}, {'en_name': 'Wuzhong', 'code': '2216', 'name': '吴中区', 'sublist': []}, {'en_name': 'Xiangcheng', 'code': '2217', 'name': '相城区', 'sublist': []}]}, '沈阳': {'en_name': 'SHENYANG', 'code': '599', 'name': '沈阳', 'sublist': [{'en_name': 'SHENYANG', 'code': '599', 'name': '沈阳', 'sublist': []}, {'en_name': 'Heping', 'code': '2126', 'name': '和平区', 'sublist': []}, {'en_name': 'Shenhe', 'code': '2127', 'name': '沈河区', 'sublist': []}, {'en_name': 'Huanggu', 'code': '2128', 'name': '皇姑区', 'sublist': []}, {'en_name': 'Dadong', 'code': '2129', 'name': '大东区', 'sublist': []}, {'en_name': 'Tiexi', 'code': '2130', 'name': '铁西区', 'sublist': []}, {'en_name': 'Dongling', 'code': '2132', 'name': '东陵区（浑南新区）', 'sublist': []}, {'en_name': 'Yuhong', 'code': '2133', 'name': '于洪区', 'sublist': []}, {'en_name': 'Shenbeixinqu', 'code': '2134', 'name': '沈北新区', 'sublist': []}, {'en_name': 'Sujiatun', 'code': '2135', 'name': '苏家屯区', 'sublist': []}, {'en_name': 'Qipanshan', 'code': '2382', 'name': '棋盘山开发区', 'sublist': []}, {'en_name': 'Xinmin', 'code': '2383', 'name': '新民市', 'sublist': []}, {'en_name': 'Liaozhong', 'code': '2384', 'name': '辽中县', 'sublist': []}, {'en_name': 'Kangping', 'code': '2385', 'name': '康平县', 'sublist': []}, {'en_name': 'Faku', 'code': '2386', 'name': '法库县', 'sublist': []}]}, '西安': {'en_name': 'XIAN', 'code': '854', 'name': '西安', 'sublist': [{'en_name': 'XIAN', 'code': '854', 'name': '西安', 'sublist': []}, {'en_name': 'Xincheng', 'code': '2070', 'name': '新城区', 'sublist': []}, {'en_name': 'Beilin', 'code': '2071', 'name': '碑林区', 'sublist': []}, {'en_name': 'Lianhu', 'code': '2072', 'name': '莲湖区', 'sublist': []}, {'en_name': 'Yanta', 'code': '2073', 'name': '雁塔区', 'sublist': []}, {'en_name': 'Weiyang', 'code': '2074', 'name': '未央区', 'sublist': []}, {'en_name': 'Baqiao', 'code': '2075', 'name': '灞桥区', 'sublist': []}, {'en_name': 'Changan', 'code': '2076', 'name': '长安区', 'sublist': []}, {'en_name': 'Yanliang', 'code': '2077', 'name': '阎良区', 'sublist': []}, {'en_name': 'Lintong', 'code': '2078', 'name': '临潼区', 'sublist': []}, {'en_name': 'Lantian', 'code': '2079', 'name': '蓝田县', 'sublist': []}, {'en_name': 'Zhouzhi', 'code': '2080', 'name': '周至县', 'sublist': []}, {'en_name': 'Hu', 'code': '2081', 'name': '户县', 'sublist': []}, {'en_name': 'Gaoling', 'code': '2082', 'name': '高陵县', 'sublist': []}, {'en_name': 'fengweixin', 'code': '2083', 'name': '沣渭新区', 'sublist': []}, {'en_name': 'Gaoxinkaifaqu', 'code': '2368', 'name': '高新技术产业开发区', 'sublist': []}, {'en_name': 'Jingjikaifaqu', 'code': '2369', 'name': '经济技术开发区', 'sublist': []}, {'en_name': 'Qujiang', 'code': '2370', 'name': '曲江新区', 'sublist': []}, {'en_name': 'Chanba', 'code': '2371', 'name': '浐灞生态区', 'sublist': []}, {'en_name': 'Yanlianghangkong', 'code': '2372', 'name': '阎良国家航空高新技术产业基地', 'sublist': []}, {'en_name': 'Minyonghangtian', 'code': '2373', 'name': '西安国家民用航天产业基地', 'sublist': []}, {'en_name': 'Guojigangwu', 'code': '2374', 'name': '国际港务区', 'sublist': []}]}, '郑州': {'en_name': 'ZHENGZHOU', 'code': '719', 'name': '郑州', 'sublist': [{'en_name': 'ZHENGZHOU', 'code': '719', 'name': '郑州', 'sublist': []}, {'en_name': 'Zhongyuan', 'code': '2194', 'name': '中原区', 'sublist': []}, {'en_name': 'Erqi', 'code': '2195', 'name': '二七区', 'sublist': []}, {'en_name': 'Guancheng', 'code': '2196', 'name': '管城区', 'sublist': []}, {'en_name': 'Jinshui', 'code': '2197', 'name': '金水区', 'sublist': []}, {'en_name': 'Huiji', 'code': '2198', 'name': '惠济区', 'sublist': []}, {'en_name': 'Zhengdongxin', 'code': '2199', 'name': '郑东新区 ', 'sublist': []}, {'en_name': 'Jingkai', 'code': '2203', 'name': '经开区', 'sublist': []}, {'en_name': 'Gaoxin', 'code': '2204', 'name': '高新区', 'sublist': []}, {'en_name': 'Shangjie', 'code': '2205', 'name': '上街区', 'sublist': []}, {'en_name': 'Xinzheng', 'code': '2399', 'name': '新郑市', 'sublist': []}, {'en_name': 'Dengfeng', 'code': '2400', 'name': '登封市', 'sublist': []}, {'en_name': 'Xinmei', 'code': '2401', 'name': '新密市', 'sublist': []}, {'en_name': 'Xingyang', 'code': '2402', 'name': '荥阳市', 'sublist': []}, {'en_name': 'Zhongmu', 'code': '2403', 'name': '中牟县', 'sublist': []}, {'en_name': 'Gongyi', 'code': '2444', 'name': '巩义市', 'sublist': []}, {'en_name': 'Hangkonggangqu', 'code': '2445', 'name': '航空港区', 'sublist': []}]}, '长沙': {'en_name': 'CHANGSHA', 'code': '749', 'name': '长沙', 'sublist': [{'en_name': 'CHANGSHA', 'code': '749', 'name': '长沙', 'sublist': []}, {'en_name': 'Changsha', 'code': '2406', 'name': '长沙县', 'sublist': []}, {'en_name': 'Furong', 'code': '2224', 'name': '芙蓉区', 'sublist': []}, {'en_name': 'Kaifu', 'code': '2227', 'name': '开福区', 'sublist': []}, {'en_name': 'Liuyang', 'code': '2408', 'name': '浏阳市', 'sublist': []}, {'en_name': 'Ningxiang', 'code': '2407', 'name': '宁乡县', 'sublist': []}, {'en_name': 'Tianxin', 'code': '2225', 'name': '天心区', 'sublist': []}, {'en_name': 'Wangcheng', 'code': '2405', 'name': '望城区', 'sublist': []}, {'en_name': 'Yuelu', 'code': '2226', 'name': '岳麓区', 'sublist': []}, {'en_name': 'Yuhua', 'code': '2228', 'name': '雨花区', 'sublist': []}]}, '重庆': {'en_name': 'CHONGQING', 'code': '551', 'name': '重庆', 'sublist': [{'en_name': 'CHONGQING', 'code': '551', 'name': '重庆', 'sublist': []}, {'en_name': 'Yuzhong', 'code': '2312', 'name': '渝中区', 'sublist': []}, {'en_name': 'Jiangbei', 'code': '2313', 'name': '江北区', 'sublist': []}, {'en_name': 'Nanan', 'code': '2314', 'name': '南岸区', 'sublist': []}, {'en_name': 'Shapingba', 'code': '2315', 'name': '沙坪坝区', 'sublist': []}, {'en_name': 'Jiulongpo', 'code': '2316', 'name': '九龙坡区', 'sublist': []}, {'en_name': 'Dadukou', 'code': '2317', 'name': '大渡口区', 'sublist': []}, {'en_name': 'Yubei', 'code': '2318', 'name': '渝北区', 'sublist': []}, {'en_name': 'Banan', 'code': '2319', 'name': '巴南区', 'sublist': []}, {'en_name': 'Beibei', 'code': '2320', 'name': '北碚区', 'sublist': []}, {'en_name': 'Wanzhou', 'code': '2321', 'name': '万州区', 'sublist': []}, {'en_name': 'Qianjiang', 'code': '2322', 'name': '黔江区', 'sublist': []}, {'en_name': 'Yongchuan', 'code': '2323', 'name': '永川区', 'sublist': []}, {'en_name': 'Fuling', 'code': '2324', 'name': '涪陵区', 'sublist': []}, {'en_name': 'Changshou', 'code': '2325', 'name': '长寿区', 'sublist': []}, {'en_name': 'Jiangjin', 'code': '2326', 'name': '江津区', 'sublist': []}, {'en_name': 'Hechuan', 'code': '2327', 'name': '合川区', 'sublist': []}, {'en_name': 'Shuangqiao', 'code': '2328', 'name': '双桥区', 'sublist': []}, {'en_name': 'Wansheng', 'code': '2329', 'name': '万盛区', 'sublist': []}, {'en_name': 'Nanchuan', 'code': '2330', 'name': '南川区', 'sublist': []}, {'en_name': 'Rongchang', 'code': '2331', 'name': '荣昌县', 'sublist': []}, {'en_name': 'Dazu', 'code': '2332', 'name': '大足县', 'sublist': []}, {'en_name': 'Bishan', 'code': '2333', 'name': '壁山县', 'sublist': []}, {'en_name': 'Tongliang', 'code': '2334', 'name': '铜梁县', 'sublist': []}, {'en_name': 'Tongnan', 'code': '2335', 'name': '潼南县', 'sublist': []}, {'en_name': 'Qijiang', 'code': '2336', 'name': '綦江县', 'sublist': []}, {'en_name': 'Zhong', 'code': '2337', 'name': '忠县', 'sublist': []}, {'en_name': 'Kai', 'code': '2338', 'name': '开县', 'sublist': []}, {'en_name': 'Yunyang', 'code': '2339', 'name': '云阳县', 'sublist': []}, {'en_name': 'Liangping', 'code': '2340', 'name': '梁平县', 'sublist': []}, {'en_name': 'Dianjiang', 'code': '2341', 'name': '垫江县', 'sublist': []}, {'en_name': 'Fengdu', 'code': '2342', 'name': '丰都县', 'sublist': []}, {'en_name': 'Fengjie', 'code': '2343', 'name': '奉节县', 'sublist': []}, {'en_name': 'Wushan', 'code': '2344', 'name': '巫山县', 'sublist': []}, {'en_name': 'Wuxi', 'code': '2345', 'name': '巫溪县', 'sublist': []}, {'en_name': 'Chengkou', 'code': '2346', 'name': '城口县', 'sublist': []}, {'en_name': 'Wulong', 'code': '2347', 'name': '武隆县', 'sublist': []}, {'en_name': 'Shizhu', 'code': '2348', 'name': '石柱县', 'sublist': []}, {'en_name': 'Xiushan', 'code': '2349', 'name': '秀山县', 'sublist': []}, {'en_name': 'Youyang', 'code': '2350', 'name': '酉阳县', 'sublist': []}, {'en_name': 'Pengshui', 'code': '2351', 'name': '彭水县', 'sublist': []}, {'en_name': 'Beibuxin', 'code': '2360', 'name': '北部新区', 'sublist': []}, {'en_name': 'Shizhu', 'code': '2433', 'name': '石柱土家族自治县', 'sublist': []}, {'en_name': 'Xiushan', 'code': '2434', 'name': '秀山土家族苗族自治县', 'sublist': []}, {'en_name': 'Youyang', 'code': '2435', 'name': '酉阳土家族苗族自治县', 'sublist': []}, {'en_name': 'Pengshui', 'code': '2436', 'name': '彭水苗族土家族自治县', 'sublist': []}]}, '哈尔滨': {'en_name': 'HAERBIN', 'code': '622', 'name': '哈尔滨', 'sublist': [{'en_name': 'HAERBIN', 'code': '622', 'name': '哈尔滨', 'sublist': []}, {'en_name': 'Acheng', 'code': '2277', 'name': '阿城区', 'sublist': []}, {'en_name': 'Bayan', 'code': '2429', 'name': '巴彦县', 'sublist': []}, {'en_name': 'Binxian', 'code': '2428', 'name': '宾\u3000县', 'sublist': []}, {'en_name': 'Daoli', 'code': '2271', 'name': '道里区', 'sublist': []}, {'en_name': 'Daowai', 'code': '2272', 'name': '道外区', 'sublist': []}, {'en_name': 'Fangzheng', 'code': '2426', 'name': '方正县', 'sublist': []}, {'en_name': 'Hulan', 'code': '2276', 'name': '呼兰区', 'sublist': []}, {'en_name': 'Mulan', 'code': '2430', 'name': '木兰县', 'sublist': []}, {'en_name': 'Nangang', 'code': '2270', 'name': '南岗区', 'sublist': []}, {'en_name': 'Pingfang', 'code': '2275', 'name': '平房区', 'sublist': []}, {'en_name': 'Songbei', 'code': '2274', 'name': '松北区', 'sublist': []}, {'en_name': 'Tonghe', 'code': '2431', 'name': '通河县', 'sublist': []}, {'en_name': 'Wuchang', 'code': '2424', 'name': '五常市', 'sublist': []}, {'en_name': 'Xiangfang', 'code': '2273', 'name': '香坊区', 'sublist': []}, {'en_name': 'Yanshou', 'code': '2432', 'name': '延寿县', 'sublist': []}, {'en_name': 'Yilan', 'code': '2427', 'name': '依兰县', 'sublist': []}]}, '无锡': {'en_name': 'WUXI', 'code': '636', 'name': '无锡', 'sublist': [{'flag': None, 'isExpand': False, 'code': '2516', 'name': '北塘区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2517', 'name': '滨湖区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2514', 'name': '崇安区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2519', 'name': '惠山区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2512', 'name': '江阴市', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2515', 'name': '南长区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2518', 'name': '无锡新区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2520', 'name': '锡山区', 'sublist': []}, {'flag': None, 'isExpand': False, 'code': '2513', 'name': '宜兴市', 'sublist': []}]}, '宁波': {'en_name': 'NINGBO', 'code': '654', 'name': '宁波', 'sublist': [{'en_name': 'Beilunqu', 'code': '3006', 'name': '北仑区', 'sublist': []}, {'en_name': 'Cixishi', 'code': '3370', 'name': '慈溪市', 'sublist': []}, {'en_name': 'Fenghuaqu', 'code': '3001', 'name': '奉化区', 'sublist': []}, {'en_name': 'Gaoxinqu', 'code': '3008', 'name': '高新区', 'sublist': []}, {'en_name': 'Haishuqu', 'code': '3003', 'name': '海曙区', 'sublist': []}, {'en_name': 'Jiangbeiqu', 'code': '3005', 'name': '江北区', 'sublist': []}, {'en_name': 'Jiangdongqu', 'code': '3004', 'name': '江东区', 'sublist': []}, {'en_name': 'Ninghaixian', 'code': '3372', 'name': '宁海县', 'sublist': []}, {'en_name': 'Xiangshanxian', 'code': '3373', 'name': '象山县', 'sublist': []}, {'en_name': 'Yinzhouqu', 'code': '3002', 'name': '鄞州区', 'sublist': []}, {'en_name': 'Yuyaoshi', 'code': '3371', 'name': '余姚市', 'sublist': []}, {'en_name': 'Zhenhaiqu', 'code': '3007', 'name': '镇海区', 'sublist': []}]}, '福州': {'en_name': 'FUZHOU', 'code': '681', 'name': '福州', 'sublist': [{'en_name': 'FUZHOU', 'code': '681', 'name': '福州', 'sublist': []}, {'en_name': 'Cangshan', 'code': '2253', 'name': '仓山区', 'sublist': []}, {'en_name': 'CHANGLE', 'code': '2472', 'name': '长乐', 'sublist': []}, {'en_name': 'FUQING', 'code': '2473', 'name': '福清', 'sublist': []}, {'en_name': 'Gulou', 'code': '2251', 'name': '鼓楼区', 'sublist': []}, {'en_name': 'Jinan', 'code': '2255', 'name': '晋安区', 'sublist': []}, {'en_name': 'Lianjiang', 'code': '2258', 'name': '连江县', 'sublist': []}, {'en_name': 'Luoyuan', 'code': '2257', 'name': '罗源县', 'sublist': []}, {'en_name': 'Mawei', 'code': '2254', 'name': '马尾区', 'sublist': []}, {'en_name': 'Minhou', 'code': '2256', 'name': '闽侯县', 'sublist': []}, {'en_name': 'Minqing', 'code': '2260', 'name': '闽清县', 'sublist': []}, {'en_name': 'Pingtan', 'code': '2261', 'name': '平潭县', 'sublist': []}, {'en_name': 'Taijiang', 'code': '2252', 'name': '台江区', 'sublist': []}, {'en_name': 'Yongtai', 'code': '2259', 'name': '永泰县', 'sublist': []}]}, '厦门': {'en_name': 'XIAMEN', 'code': '682', 'name': '厦门', 'sublist': [{'en_name': 'XIAMEN', 'code': '682', 'name': '厦门', 'sublist': []}, {'en_name': 'Haicang', 'code': '2267', 'name': '海沧区', 'sublist': []}, {'en_name': 'Huli', 'code': '2265', 'name': '湖里区', 'sublist': []}, {'en_name': 'Jimei', 'code': '2266', 'name': '集美区', 'sublist': []}, {'en_name': 'Siming', 'code': '2264', 'name': '思明区', 'sublist': []}, {'en_name': 'Tongan', 'code': '2268', 'name': '同安区', 'sublist': []}, {'en_name': 'Xiangan', 'code': '2269', 'name': '翔安区', 'sublist': []}]}, '石家庄': {'en_name': 'SHIJIAZHUANG', 'code': '565', 'name': '石家庄', 'sublist': [{'en_name': 'SHIJIAZHUANG', 'code': '565', 'name': '石家庄', 'sublist': []}, {'en_name': 'Changan', 'code': '2288', 'name': '长安区', 'sublist': []}, {'en_name': 'Dongkaifaqu', 'code': '2293', 'name': '东开发区', 'sublist': []}, {'en_name': 'gaochengshi', 'code': '2296', 'name': '藁城市', 'sublist': []}, {'en_name': 'Gaoyi', 'code': '2418', 'name': '高邑县', 'sublist': []}, {'en_name': 'Jingxing', 'code': '2420', 'name': '井陉县', 'sublist': []}, {'en_name': 'Jingxingkuangqu', 'code': '2294', 'name': '井陉矿区', 'sublist': []}, {'en_name': 'Jinzhoushi', 'code': '2297', 'name': '晋州市', 'sublist': []}, {'en_name': 'Lingshou', 'code': '2414', 'name': '灵寿县', 'sublist': []}, {'en_name': 'Luancheng', 'code': '2412', 'name': '栾城县', 'sublist': []}, {'en_name': 'Luquanshi', 'code': '2299', 'name': '鹿泉市', 'sublist': []}, {'en_name': 'Pingshan', 'code': '2301', 'name': '平山县', 'sublist': []}, {'en_name': 'Qiaodong', 'code': '2289', 'name': '桥东区', 'sublist': []}, {'en_name': 'Qiaoxi', 'code': '2290', 'name': '桥西区', 'sublist': []}, {'en_name': 'Shenze', 'code': '2415', 'name': '深泽县', 'sublist': []}, {'en_name': 'Wuji', 'code': '2416', 'name': '无极县', 'sublist': []}, {'en_name': 'Xingtang', 'code': '2413', 'name': '行唐县', 'sublist': []}, {'en_name': 'Xinhua', 'code': '2291', 'name': '新华区', 'sublist': []}, {'en_name': 'Xinjishi', 'code': '2295', 'name': '辛集市', 'sublist': []}, {'en_name': 'Xinleshi', 'code': '2298', 'name': '新乐市', 'sublist': []}, {'en_name': 'Yuanshi', 'code': '2302', 'name': '元氏县', 'sublist': []}, {'en_name': 'Yuhua', 'code': '2292', 'name': '裕华区', 'sublist': []}, {'en_name': 'Zanhuang', 'code': '2419', 'name': '赞皇县', 'sublist': []}, {'en_name': 'Zhaoxian', 'code': '2417', 'name': '赵县', 'sublist': []}, {'en_name': 'Zhengding', 'code': '2300', 'name': '正定县', 'sublist': []}]}, '合肥': {'en_name': 'HEFEI', 'code': '664', 'name': '合肥', 'sublist': [{'en_name': 'HEFEI', 'code': '664', 'name': '合肥', 'sublist': []}, {'en_name': 'Baohe', 'code': '2355', 'name': '包河区', 'sublist': []}, {'en_name': 'Beichengxinqu', 'code': '2438', 'name': '北城新区', 'sublist': []}, {'en_name': 'Binhuxinqu', 'code': '2357', 'name': '滨湖新区', 'sublist': []}, {'en_name': 'Gaoxinqu', 'code': '2359', 'name': '高新区', 'sublist': []}, {'en_name': 'Jingjijishukaifaqu', 'code': '2356', 'name': '经济技术开发区', 'sublist': []}, {'en_name': 'Luyang', 'code': '2352', 'name': '庐阳区', 'sublist': []}, {'en_name': 'Shushan', 'code': '2354', 'name': '蜀山区', 'sublist': []}, {'en_name': 'Xinzhanzonghekaifashiyanqu', 'code': '2358', 'name': '新站综合开发试验区', 'sublist': []}, {'en_name': 'Yaohai', 'code': '2353', 'name': '瑶海区', 'sublist': []}, {'en_name': 'Zhengwuwenhuaqu', 'code': '2437', 'name': '政务文化新区', 'sublist': []}]}, '惠州': {'en_name': 'HUIZHOU', 'code': '773', 'name': '惠州', 'sublist': [{'en_name': 'Boluoxian', 'code': '3255', 'name': '博罗县', 'sublist': []}, {'en_name': 'Dayawanqu', 'code': '3254', 'name': '大亚湾区', 'sublist': []}, {'en_name': 'Huicheng', 'code': '2246', 'name': '惠城区', 'sublist': []}, {'en_name': 'Huidongxian', 'code': '3256', 'name': '惠东县', 'sublist': []}, {'en_name': 'Huiyang', 'code': '2247', 'name': '惠阳区', 'sublist': []}, {'en_name': 'Longmenxian', 'code': '3257', 'name': '龙门县', 'sublist': []}, {'en_name': 'Zhongkaiqu', 'code': '3253', 'name': '仲恺区', 'sublist': []}]}}

def find_city(city_name):
    return hot_citys[city_name]

def find_city_code(city_name):
    return find_city(city_name).get('code')

def find_areas(city_name = None, city = None):
    if city_name is not None:
        city = find_city(city_name)

    city_code = city.get('code')
    areas = city.get('sublist')
    for area in areas:
        if area.get('code') == city_code:
            areas.remove(area)
    return areas


def flat_list(original ):
    new_list = []
    for item in original:
        if isinstance(item, (list, tuple, set,)):
            new_list.extend(flat_list(item))
        else:
            new_list.append(item)
    return new_list

def find_areas_codes(city_name = None, city = None):
    if city_name is not None:
        city = find_city(city_name)

    city_code = city.get('code')
    areas = city.get('sublist')
    for area in areas:
        if area.get('code') == city_code:
            areas.remove(area)
    return [ area.get('code') for area in areas]

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
        self.header = headers
        self.browser = None
        self.headless = headless
        self.html = None
        self.city_names = city_names
        self.job_names = job_names
        self.city_urls = None
        self.area_urls = None
        self.city_urls_template = "https://sou.zhaopin.com/?jl={city_code}&kw={keyword}&kt=3"
        self.area_urls_template = "https://sou.zhaopin.com/?jl={city_code}&re={area_code}&kw={keyword}&kt=3"

    def __enter__(self):
        #executable_path = {'executable_path':'C:\\Program Files\\Firefox\\firefox.exe'}
        #chrome_options = Options()
        #chrome_options.add_argument('disable-infobars')
        #chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        #self.browser = Browser("firefox", headless=self.headless, options=chrome_options)
        #self.browser = Browser("firefox", headless=self.headless)
        options = webdriver.FirefoxOptions()
        # 下面这个方法已经不建议使用
        #options.set_headless(True)
        options.headless = self.headless
        # 不使用gpu
        # -private
        #options.add_argument(argument="--disable-gpu")
        #options.add_argument(argument="-private")
        # self.browser = webdriver.Firefox(firefox_options=options, executable_path="")
        self.browser = webdriver.Firefox(options=options)
        #browser.get('http://www.baidu.com/')


        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.browser:
            pass
            #self.browser.quit()

    def visit(self, url):
        self.browser.get(url)
        #tag = self.browser.find_by_text('行政区')

        #self.html = self.browser.page_source

        #return BeautifulSoup(self.html, 'html.parser')

    def find_by_text(self, text):
        return self.browser.find_by_xpath(
            '//a[text()="{}"]'.format(text),
            original_find="link by text",
            original_query=text,)

    def find_by_id(self, id):
        return self.browser.find_element_by_id(id)

    # 生成城市的访问的url
    def gen_city_url(self):
        self.city_urls = []
        for kw in self.job_names:
            for city in self.city_names:
                city_code = find_city_code(city)
                _url = self.city_urls_template.format(city_code=city_code, keyword=kw)
                self.city_urls.append((kw, _url))
        return self.city_urls

    # 城市各个行政区的url
    def gen_area_url(self):
        self.area_urls = []
        for city in [find_city(city) for city in self.city_names]:
            city_code = city.get('code')
            area_codes = find_areas_codes(city=city)
            for area_code in area_codes:
                for kw in self.job_names:
                    self.area_urls.append(
                    self.area_urls_template.format(city_code=city_code, area_code=area_code, keyword=kw, ))


        return self.area_urls


    def parse_job_list(self):

        '''
        解析搜索结果
        :return:
        '''
        #print(self.browser.page_source)

        try:
            login_window = WebDriverWait(self.browser, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "a-dialog"))
            )
            if login_window:
                login_window.find
        except :
            pass

        list_div = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, "listContent"))
        )

        job_links = list_div.find_elements_by_tag_name('a')
        for a in job_links:
            print(a.get_attribute('href'))



    def next_page(self):
        soupager = self.browser.find_element_by_class_name('soupager')




if __name__ == '__main__':

    with ZhaopinSpider(headless=False, city_names=('天津','北京',) , job_names=("hadoop",)) as spider:

        # 为了跳过第一次访问的警告框
        spider.visit("https://sou.zhaopin.com/?jl=530&re=2002&kw=java&kt=3")
        try:
            print(spider.browser.get_cookies())
            list_div = WebDriverWait(spider.browser, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "risk-warning__content"))
            )

            button = list_div.find_element_by_tag_name('button')
            button.click()
            #spider.visit("https://sou.zhaopin.com/?jl=530&re=2002&kw=java&kt=3")
        except TimeoutException as ex:
            pass

        #print(self.browser.get_cookies())

        urls = spider.gen_area_url()
        for url in urls:
            print(url)

        spider.visit("https://sou.zhaopin.com/?jl=530&re=2002&kw=java&kt=3")
        spider.parse_job_list()