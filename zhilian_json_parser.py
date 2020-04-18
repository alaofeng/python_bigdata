
import json

with open('zhilian.json','r') as f:
    data = json.load(fp=f)
    location = (data.get('basic').get('dict').get('location'))
    print(location)
    #dict_keys(['province', 'all', 'other', 'hotcitys'])
    print(location.keys())
    hotcitys = location['hotcitys']
    #print(hotcitys)
    citys = {}
    for city in hotcitys:
        print(city)
        citys[city['name']] = city

    print(citys)

