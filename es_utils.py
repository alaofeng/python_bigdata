import json
from file_query import ES


if __name__ == '__main__':
    # index = "local_file_index"#
    index = "orico_file_index"
    es = ES("127.0.0.1:9200", index)
    resp = es.create_index("box_schema.json", force=True)
    #ES.reindex(es.es, "local_file", index,es.es)