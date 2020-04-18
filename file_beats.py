# -*- coding: utf-8 -*-
# 导入系统组件
import os
import time
from datetime import datetime
from tikapp import TikaApp
import gevent
from gevent import monkey; monkey.patch_all()
import traceback
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json


class FileBeats:
    # # 建立文件索引
    #只有如下扩展名的文件才会被索引文件内容
    export_content_exts = (
        '.md', '.html','.htm','.txt', '.ppt', '.pptx', '.key', '.pdf', ".pages", ".doc", ".docx", '.py', '.java')

    def __init__(self
                 , index
                 , es_host="localhost:9200"
                 , file_jar='/Users/laofeng/es_home/tika-app-1.23.jar'
                 , index_content= False
                 , create_index = True
                 , force_renew_index = False
                 , schema_file = None):

        self.tika_app = TikaApp(file_jar)
        self.es = Elasticsearch(es_host)
        self.index=index
        self.index_content = index_content

        #查询索引是否存在
        index_exist = self.es.indices.exists(index)

        #if not index_exist and not create_index:

        if not index_exist and create_index and schema_file:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
                self.es.indices.create(index, schema)


        #如果已经存在，且强制renew，先删除后，再建立
        if index_exist and force_renew_index:
            self.es.indices.delete(index)
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
                self.es.indices.create(index, schema)

    # 格式化时间，参数是秒和时间格式
    @staticmethod
    def second2date(second, style="%Y-%m-%d %H:%M:%S"):
        time_array = time.localtime(second)
        date_str = time.strftime(style, time_array)
        return date_str

    def export_file_tags(self, abs_path):
        tags = {"path": abs_path}
        (basename, ext) = os.path.splitext(abs_path)
        tags['ext'] = ext.lstrip('.')  # 去掉了后缀的点
        tags['name'] = os.path.basename(abs_path)
        size = os.path.getsize(abs_path)
        tags['size'] = size

        # 过滤调太大或者太小的文件
        # 文件太大，二进制文件类型不导出content

        if self.index_content and ext.lower() in FileBeats.export_content_exts:
            try:
                r = self.tika_app.extract_only_content(path=abs_path, payload="base64_payload")
                if r:
                    tags['content'] = r
            except Exception as e:
                traceback.print_exc()
        return tags

    # 索引文档
    def index_doc(self, tags, _type='_doc'):
        # index 相当于表名， body被索引的文本（分词）
        tags['timestamp'] = datetime.now()
        # 使用文件全路径做为id
        res = self.es.index(index=self.index, doc_type=_type, body=tags, id=tags['path'])

    def index_docs(self, docs):
        for doc in docs:
            self.index_doc(doc)

    # 处理一个文件，先导出tags，然后索引文档
    def process_file(self, f):
        tags = self.export_file_tags(f)
        self.index_doc(tags)


    def beats_more(self, folders, asynchronous=True):
        print("开始索引文件", FileBeats.second2date(time.time()))
        for folder in folders:
            self.start_beats(folder)

        print("索引文件结束", FileBeats.second2date(time.time()))


    def start_beats(self, source_dir = '/Volumes/portable/sync/', asynchronous=True):
        print("开始索引文件", source_dir, FileBeats.second2date(time.time()))
        # 遍历文件
        greenlets = list()
        #index_tasks = list()

        for folder, dirs, files in os.walk(source_dir, topdown=False):
            # 过滤掉一些文件夹

            if '@' in folder or '.svn' in folder or folder.endswith('.app') or "迅雷" in folder:
                print('忽略目录', folder)
                continue
            for f in files:
                if f.startswith("."):
                    continue
                abs_path = os.path.join(folder, f)
                try:
                    # process_file(abs_path)
                    if asynchronous:
                        greenlets.append(gevent.spawn(self.export_file_tags, abs_path))
                    else:
                        tags = self.export_file_tags(abs_path)
                        self.index_doc(tags)
                    # 任务达到500个，执行一次
                    if len(greenlets) >= 5:
                        gevent.joinall(greenlets)
                        self.index_docs([g.value for g in greenlets])
                        # 使用并发es会出现一个read timeout或者是socket的错误
                        # index_tasks.append(gevent.spawn(index_docs,[g.value for g in greenlets]))
                        greenlets.clear()
                    # if len(index_tasks) > 50:
                    #     gevent.joinall(index_tasks)
                    #     index_tasks.clear()
                except Exception as e:
                    traceback.print_exc()
        # 清理不足5个文件的情况
        if asynchronous:
            gevent.joinall(greenlets)
            self.index_docs([g.value for g in greenlets])
        # index_tasks.append(gevent.spawn(index_docs, [g.value for g in greenlets]))
        # gevent.joinall(index_tasks)

        print("索引文件结束", source_dir, FileBeats.second2date(time.time()))





if __name__ == '__main__':
    source_dirs = ("/Volumes/T1","/Volumes/T3", "/Volumes/red3","/Volumes/media")

    beats = FileBeats("box_file_index", schema_file="box_schema.json", index_content=False)
    beats.beats_more(source_dirs[0:1],asynchronous=True)

