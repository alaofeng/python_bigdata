import time
import datetime
import dateutil
'''
格式 含义

%a 本地（locale）简化星期名称

%A 本地完整星期名称

%b 本地简化月份名称

%B 本地完整月份名称

%c 本地相应的日期和时间表示

%d 一个月中的第几天（01 - 31）

%H 一天中的第几个小时（24小时制，00 - 23）

%I 第几个小时（12小时制，01 - 12）

%j 一年中的第几天（001 - 366）

%m 月份（01 - 12）

%M 分钟数（00 - 59）

%p 本地am或者pm的相应符

%S 秒（01 - 61）

%U 一年中的星期数。（00 - 53星期天是一个星期的开始。）第一个星期天之前的所有天数都放在第0周。

%w 一个星期中的第几天（0 - 6，0是星期天）

%W 和%U基本相同，不同的是%W以星期一为一个星期的开始。

%x 本地相应日期

%X 本地相应时间

%y 去掉世纪的年份（00 - 99）

%Y 完整的年份

%Z 时区的名字（如果不存在为空字符）

%% ‘%’字符
'''


def gen_file_name():

    return "{}.json".format(time.strftime('%Y%m%d%H%M%S', time.localtime()))

if __name__ == '__main__':
    print(time.time())
    print(time.localtime())

    print(time.strftime('%Y%m%d%H%M%S' , time.localtime()))

    print(gen_file_name())