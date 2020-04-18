# -*- coding: utf-8 -*-
# 导入系统组件
import json
from elasticsearch import Elasticsearch


#
class ES:

    #重新索引
    @staticmethod
    def reindex(source_client, source_index, dest_index, dest_client=None,  query=None):

        body = {"query": {"match_all": {}}}

        helpers.reindex(client=source_client,
                        source_index=source_index,
                        target_index=dest_index,
                        target_client=dest_client,
                        query=body)

    def __init__(self, es_host='localhost:9200', index_name = 'local_file_index'):

        self.es = Elasticsearch('localhost:9200')
        self.index_name = index_name

    # 创建索引
    def create_index(self, schame_file="es_schema.json", force=False):

        # :arg index_name: 创建索引的名称
        # :arg force: 如果索引已经存在是否删除索引，default:False

        index_name = self.index_name
        if self.es.indices.exists(index_name):
            print("索引已经存在:", index_name)
            if force:
                self.es.indices.delete(index_name)
                print("索引已经删除存在:", index_name)
            else:
                return

        with open(schame_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
            self.es.indices.create(index_name, schema)

    # 使用查询字符串，没有打分
    def q(self, q_str, size = 10, from_ = 0):
        # _body: Query DSL
        # index: _all 或者 empty都代表搜索所有的索引，也可以指定特定的索引
        # _source: 默认True，是否显示source字段
        # size：取回多少文档
        # from_:开始获取文档的位置（偏移量），和size参数结合可以实现分页
        # _source_excludes：列表，排除_source里的字段
        # _source_includes：列表，取回_source里的包含的字段
        # q: Query in the Lucene query string syntax
        # resp = self.es.search(q=q_str, index=self.index_name, _source=True, size=size, from_=from_, _source_includes=['path'])
        resp = self.es.search(q=q_str, index=self.index_name, _source=True, size=size, from_=from_,
                              _source_includes=['path'])
        return resp

    #查询
    def search(self, keyword,size = 10, exts=None , _sorts = None , from_ = 0, _source = True, highlight_ = True, explain_=False):

        # body = {
        #     "query": {
        #         "bool":{
        #              "should" : [
        #                  { "match" : { "path" : keyword} },
        #                  { "match" : { "content" : keyword } }
        #              ]
        #         }
        #     },
        #     "highlight": {
        #         "fields": {
        #             "path": {},
        #             "content": {}
        #         }
        #     }
        # }

        body = {
            "track_total_hits": True,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"path": keyword}},
                        {"match": {"content": keyword}},
                    ]
                }
            }
        }
        if _sorts:
            sorts = []
            for s in _sorts.split(','):
                arr = s.split(":")
                if len(arr) == 1:
                    sorts.append(arr[0])
                elif len(arr) == 2:
                    sorts.append({arr[0] : arr[1]})
            body['sort'] = sorts

        if highlight_:

            body["highlight"] = {
                "pre_tags": ["<span class='highlight'>"],
                "post_tags": ["</span>"],
                "fields": {
                    "path": {},
                    "content": {}
                }
            }
        if exts and len(exts) > 0:
            body['query']['bool']['filter'] = {"terms": {'ext': exts } }

        resp = self.es.search(body, index=self.index_name
                              , _source=_source
                              , size=size
                              , from_=from_
                              ,_source_includes=['path', 'ext','size','name', 'content']
                              ,explain=explain_
                              )
        self.es.count()
        total = resp['hits']['total']['value']

        if total > 0:
            return total, resp['hits']['hits']
        else:
            return 0, None

        # 查询
    def query_ext(self, ext, size=20, from_=0):
        body = {
            "track_total_hits": True,
            "query": {
                    "bool": {
                        "filter": [
                            {"term": {"ext": ext}}
                        ]
                    }
                }
            }


        resp = self.es.search(body, index=self.index_name
                                  , _source=False
                                  , size=size
                                  , from_=from_
                                  )
        return resp


    #注意后缀名，应该没有想象的那样可以索引后缀名
    def query_ext(self, ext, size=20, from_=0):

        body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"ext": ext}}
                        ]
                    }
                }
            }


        resp = self.es.search(body, index=self.index_name
                                  , _source=False
                                  , size=size
                                  , from_=from_
                                  )
        return resp

    # 统计每个后缀名，文件的数量. 使用term聚合实现
    def distinct(self, field='ext'):
        #
        body = {
            "track_total_hits": True,
            "aggs": {
                "ext_count": {
                    "terms": {"field": field,"size": 10000}
                }
            }
        }

        resp = self.es.search(body, index=self.index_name, _source=False, size = 0)
        #print(json.dumps(resp, indent=2, ensure_ascii=False))
        #return resp['hits']['total']['value'], resp['aggregations']['ext_count']['buckets']
        return resp

        # 统计每个后缀名，文件的数量. 使用term聚合实现
    def distinct2(self, field='ext'):
        body = {
            "seq_no_primary_term": True,
            "query": {"match_all": {}},
            "collapse" : {
                "field" : field,
                "max_concurrent_group_searches": 4
            },
            "size": 100,
            "_source": False,
        }


        resp = self.es.search(body, index=self.index_name)
        # print(json.dumps(resp, indent=2, ensure_ascii=False))
        return resp

    def count(self, index_name = None):
        if not index_name:
            return self.es.count()
        else:
            return self.es.count(index_name)


    def index_names(self):
        return  self.es.indices.stats()['indices'].keys()

    def index_count(self):
        indexs = self.es.indices.stats()['indices']
        result = dict()
        for  k in indexs.keys():
            result[k] = indexs[k]['primaries']['docs']['count']

        return result



if __name__ == "__main__":
    es = ES(index_name='box_file_index')

    #print(es.count())
    from threading import Timer
    # import time
    # while 1:
    #     time.sleep(5)
    #     print(es.index_count())

    # resp = (es.distinct("ext"))
    # print(json.dumps(resp, indent=2, ensure_ascii=False))


    ##'_shards', '_all', 'indices']
    #print(es.es.indices.stats(metric='indexing'))

    # print(json.dumps(es.es.indices.stats()['indices'].keys(), indent=2, ensure_ascii=False))
    #resp = es.q("elasticsearch")
    #print(json.dumps(resp, indent=2, ensure_ascii=False))
    #在path和content中查询关键字并过滤文件的扩展名,
    resp = es.search("MOV", size=10, _source=True, explain_=False)
    print(json.dumps(resp, indent=2, ensure_ascii=False))

    resp = es.query_ext('MOV',size=0)
    print(json.dumps(resp, indent=2, ensure_ascii=False))

    resp = es.distinct(field = 'ext')
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    print(es.index_count())

