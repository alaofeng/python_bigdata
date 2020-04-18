# coding=utf-8
from flask import Flask, render_template, request, jsonify
import json
import time
from file_query import ES
# import logging

class CustomFlask(Flask):
    '''
    テンプレートのデリミタがVue.jsと競合するので、Flask側でデリミタを別の文字に変更する
    因为jinja模板分隔符与Vue.js冲突，更改jinjia的分割符
	参照：https://muunyblue.github.io/0b7acbba52fb92b2e9c818f7f56bac99.html
    '''
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
		block_start_string='(%',
		block_end_string='%)',
		variable_start_string='((',
		variable_end_string='))',
		comment_start_string='(#',
		comment_end_string='#)',
    ))

app = CustomFlask(__name__)
es = ES()
#app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False    # jsonifyで日本語が文字化けする場合の対処
app.DEBUG = True
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ロギング
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s %(levelname)-8s %(module)-18s %(funcName)-10s %(lineno)4s: %(message)s'
# )


@app.route("/ext_count")
def ext_count():
	resp=es.distinct("ext")
	return json.dumps(resp, indent=2, ensure_ascii=False)

@app.route("/search", methods=["GET", "POST"])
def search():
	data = request.get_json(silent=True)

	keyword = data['keyword']
	page_num = int(data['page_num'])
	page_size = int(data['page_size'])
	# print(request.method)  # 获取访问方式 GET
	# print(request.url)  # 获取url http://127.0.0.1:5000/req?id=1&name=wl
	# print(request.cookies)  # 获取cookies {}
	# print(request.path)  # 获取访问路径 /req
	# print(request.args)  # 获取url传过来的值  ImmutableMultiDict([('id', '1'), ('name', 'wl')])
	# print(request.args.to_dict())  # 获取到一个字典 {'id': '1', 'name': 'wl'}
	resp = es.search(keyword, size=page_size, from_= page_num * page_size - 1)
	total = resp[0]
	if total > 0:
		docs = []
		for item in resp[1]:
			doc = dict()
			doc['_score'] = item['_score']
			doc['name'] = item['_source']['name']
			doc['size'] = item['_source']['size']
			doc['ext'] = item['_source']['ext']

			highlight = item['highlight']

			path = highlight.get("path")
			if path:
				doc['path'] = path[0]
			else:
				doc['path'] = item['_id']

			content = highlight.get('content')
			if content:
				doc['content'] = content[0]
			else:
				content = item['_source'].get('content', "None")
				doc['content'] = content[0:100]

			docs.append(doc)

	return json.dumps((total,docs,1), indent=2, ensure_ascii=False)

@app.route("/")
def index():
	'''
	画面
	'''
	return render_template("index.html", current_time=time.time())

# @app.route("/get")
# def get():
# 	'''
# 	ISBNに対応する書籍情報の取得
# 	'''
# 	# パラメータからISBNコードを取得
# 	isbn = request.args.get('isbn', default=None)
# 	# 必要な情報を取得する
# 	json_data = openBD().get_json(isbn) if isbn else {}
# 	# dict型をJSON型のレスポンスに変換
# 	response = jsonify(json_data)
#
# 	return response

@app.route("/regist")
def regist():
	'''
	ISBNに対応する書籍情報を取得して、Elasticsearchに登録
	'''
	# パラメータからISBNコードを取得
	isbn = request.args.get('isbn', default=None)
	# logging.debug(isbn)



	# 必要な情報を取得する
	#json_data = openBD().get_json(isbn) if isbn else {}

	
	json_data = {}
	json_data['isbn'] = isbn
	json_data['title'] = 'ES构架自己的搜索引擎'
	json_data['publisher'] = 'xxx出版社'
	json_data['pubdate'] = '2019-12-31'
	json_data['cover'] = 'None'
	json_data['author'] = 'laofeng'
	json_data['dummy'] = '1'
	# if len(json_data) > 0:
	# 	# Elasticsearch
	# 	es = ElasticsearchWrapper('openbd', 'openbd-index')
	#
	# 	json_data["dummy"] = "1"
	# 	# 追加
	# 	es.insert_one(json_data)


	response = jsonify(json_data)
	print(response)
	return response

# @app.route("/search")
# def search():
# 	'''
# 	検索
# 	'''
# 	# パラメータからISBNコードを取得
# 	isbn = request.args.get('isbn', default=None)
# 	title = request.args.get('title', default=None)
# 	publisher = request.args.get('publisher', default=None)
# 	pubdate = request.args.get('pubdate', default=None)
# 	cover = request.args.get('cover', default=None)
# 	author = request.args.get('author', default=None)
#
# 	# 検索の項目名、項目値のDictionary
# 	items = {}
# 	if isbn != None:
# 		items['isbn'] = isbn
# 	if title != None:
# 		items['title'] = title
# 	if publisher != None:
# 		items['publisher'] = publisher
# 	if pubdate != None:
# 		items['pubdate'] = pubdate
# 	if cover != None:
# 		items['cover'] = cover
# 	if author != None:
# 		items['author'] = author
#
# 	# Elasticsearch
# 	es = ElasticsearchWrapper('openbd', 'openbd-index')
# 	# 検索
# 	json_data = es.search_and(items)
#
# 	# dict型をJSON型のレスポンスに変換
# 	response = jsonify(json_data)
#
# 	return response

# @app.route("/list")
# def list():
# 	'''
# 	検索
# 	'''
# 	# 検索の項目名、項目値のDictionary
# 	items = {}
# 	items["dummy"] = "1"
#
# 	# Elasticsearch
# 	es = ElasticsearchWrapper('openbd', 'openbd-index')
# 	# 検索
# 	json_data = es.search_and(items)
#
# 	# dict型をJSON型のレスポンスに変換
# 	response = jsonify(json_data)
#
# 	return response

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=8080)
