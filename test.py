# coding=utf-8
from elasticsearch import Elasticsearch
import json

if __name__ == "__main__":
    es = Elasticsearch("127.0.0.1:9200")
    resp = es.ping()
    print(resp)

    resp = es.cat.health()
    print(resp)

    resp = es.cat.aliases()
    print(resp)

    resp = es.cat.allocation()
    print(resp)

    resp = es.cat.count()
    print(resp)

    resp = es.cat.plugins()
    print(resp)

    #返回类型是str
    resp = es.cat.indices()
    print(resp)

    #返回类型是str
    resp = es.cat.help()
    print(resp)

    resp = es.info()
    print(resp)




    print( json.dumps(resp,indent = 2, ensure_ascii = False))

    index_name = "local_file"
    body = {
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    },
                    "ext": {
                        "type": "keyword"
                    },
                    "path": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    }
                }
            }
        }

    #resp = es.indices.create(index=index_name, body= body )
    #print(json.dumps(resp, indent=2, ensure_ascii=False))

    #resp = es.indices.exists(index_name)
    #print(resp)

    #resp = es.indices.delete("local_file")
    #print(resp)
    resp = es.indices.get(index_name)
    print(json.dumps(resp, indent=2, ensure_ascii=False))

