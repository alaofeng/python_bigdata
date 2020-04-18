# 必须要安装的包， kazoo、thrift、happybase
import hbase
from hbase import namespace
from hbase import table
from hbase import Connection
from hbase import ColumnFamilyAttributes
import traceback
import random





def conn_callback(zk, func, **kwargs):
    with hbase.ConnectionPool(zk).connect() as conn:
        print("连接到hbase")
        if kwargs is not None and len(kwargs) > 0:
            func(conn, kwargs)
        else:
            func(conn)
    print("连接断开")

def hbase_info(conn):

    ns_names = conn.namespaces()
    for ns_name in ns_names:
        #ns_name是一个字符串类型
        print(ns_name, type(ns_name))
        ns = conn.namespace(ns_name)
        print("\t当前的空间的表：P{}" % ns.tables())

def create_table(conn, ns_="default", table_name=None, families=None):
    '''
    def __init__(self,
                 name,
                 versions=b'1',
                 min_versions=b'0',
                 compression=b'NONE',
                 keep_deleted_cells=b'FALSE',
                 blockcache=b'true',
                 blocksize=b'65536',
                 in_memory=b'false'):
    '''
    ns = conn[ns_]

    cols = []
    cols.append(ColumnFamilyAttributes('base', versions=b'3'))
    cols.append(ColumnFamilyAttributes('ext',versions=b'3'))
    try:
        ns.create_table(table_name, families=cols)
    except hbase.exceptions.TableExistsError as err:
        # 表已经存在的异常
        traceback.print_exc()

# 这个callback只返回一个结果，是否成功
def put_callback(is_success):
    print("put数据结果：%s"  % is_success)

def put(conn, ns='default' , table_name=None, row=None, callback=put_callback):
    t:table = conn[ns][table_name]
    t.put(row, callback)



def get(conn, ns='default', table_name='person', key='00001'):
    t: table = conn[ns][table_name]
    row = t.get(key)
    return row

def scan(conn, ns='default', table_name='person'):
    t: table = conn[ns][table_name]
    # scan方法返回的是一个游标变量
    for row in t.scan():
        yield row



if __name__ == '__main__':
    zk = 'localhost:2181'
    ns = "laofeng"
    table_name = "person"
    #conn_callback(zk, hbase_info)
    with hbase.ConnectionPool(zk).connect() as conn:
        print("连接到hbase")
        create_table(conn, ns_=ns, table_name=table_name)

        print("插入一条数据")
        for i in range(2,100):
            put(conn, ns=ns, table_name=table_name, row=hbase.Row(
            # row key
            "0000%d" % i ,{
            "base:name":b"lily%d" % i,
            "base:age":b'%d' % random.randint(10,50),
            "ext:phone_no":b'12345678901'
            }
        ))
        row = get(conn, ns=ns, table_name=table_name, key='00001')
        print(row)

        #f是一个生成器函数
        f = scan(conn, ns=ns, table_name=table_name)
        print(f)
        for row in f:
            print(row)

    print("连接断开")


