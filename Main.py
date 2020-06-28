# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import json
import time
from elasticsearch import Elasticsearch

#todo
#自动建立stock和checkpoint的时间分片index
#结束后force merge位一个segment，并且设置index为只读

index_name = "stock-2020-06-23"
date_str = "2020-06-23"
timeArray = time.strptime(date_str, '%Y-%m-%d')
current_time = int(time.mktime(timeArray))
checkpoint_name = "checkpoint-2020-06-23"
checkpoint_separator_symbol = "$$"


def get_concept_area_id(es_client):
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    concept_array = resp.json()[1][0][1][3][1]
    concept_area = []
    for concept in concept_array:
        id = concept[0] + checkpoint_separator_symbol + concept[2]
        data = {
            "type": 1,
            "check": 0
        }
        es_client.index(index=checkpoint_name, body=data, id=id)


def get_industry_area_id(es_client):
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    industry_array = resp.json()[1][0][1][4][1]
    industry_area = []
    for industry in industry_array:
        id = industry[0] + checkpoint_separator_symbol + industry[2]
        data = {
            "type": 2,
            "check": 0
        }
        es_client.index(index=checkpoint_name, body=data, id=id)


def get_location_area_id(es_client):
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    location_array = resp.json()[1][0][1][5][1]
    location_area = []
    for location in location_array:
        id = location[0] + checkpoint_separator_symbol + location[2]
        data = {
            "type": 3,
            "check": 0
        }
        es_client.index(index=checkpoint_name, body=data, id=id)


def get_area_stock_data(node):
    area_data = []
    page = 1
    while (True):
        time.sleep(4)
        url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=" + str(
            page) + "&num=40&sort=symbol&asc=1&node=" + node + "&symbol=&_s_r_a=init"
        # url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=" + str(page) + "&num=40&sort=symbol&asc=1&node=chgn_700682&symbol=&_s_r_a=auto"
        resp = requests.get(url)
        print(url)
        print(resp.text)
        try:
            json_result = resp.json()
            print(json_result)
        except Exception:
            break
        if not json_result:
            break
        for stock in json_result:
            stock['name'] = stock['name'].encode('utf-8')
            area_data.append(stock)
        page = page + 1
    return area_data


def save_area_data_to_es(area_data, area_name, area_id, es_client):
    for stock in area_data:
        exist = True
        stock_doc = {}
        try:
            stock_doc = es_client.get(index_name, id=stock["symbol"])
        except Exception as ex:

            if ex.status_code == 404:
                exist = False
        if exist:
            if area_id == 1:
                if area_name not in stock_doc['_source']['concept_area']:
                    stock_doc['_source']['concept_area'].append(area_name)
            if area_id == 2:
                if area_name not in stock_doc['_source']['industry_area']:
                    stock_doc['_source']['industry_area'].append(area_name)
            if area_id == 3:
                if area_name not in stock_doc['_source']['location_area']:
                    stock_doc['_source']['location_area'].append(area_name)
            es_client.index(index=index_name, body=stock_doc['_source'], id=stock_doc['_id'])
        else:
            data = {
                "symbol": stock['symbol'],
                "name": stock['name'],
                "percent": float(stock['changepercent']),
                "industry_area": [area_name] if area_id == 2 else [],
                "concept_area": [area_name] if area_id == 1 else [],
                "location_area": [area_name] if area_id == 3 else [],
                "body": json.dumps(stock),
                "date": current_time
            }
            es_client.index(index=index_name, body=data, id=stock['symbol'])
        print("finish the index:[%s]" % stock['symbol'])

def get_area_data(type):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "type": {
                                "value": type
                            }
                        }
                    }, {
                        "term": {
                            "check": {
                                "value": 0
                            }
                        }
                    }
                ]
            }
        },
        "size": 10000
    }
    area_data = es.search(body=body, index=checkpoint_name)
    return area_data["hits"]["hits"]

def save_checkpoint(name, node, type):
    id = name + checkpoint_separator_symbol + node
    data = {
        "type": type,
        "check": 1
    }
    es.index(index=checkpoint_name, body=data, id=id)

if __name__ == '__main__':

    es = Elasticsearch(hosts="http://localhost:9200")
    get_concept_area_id(es)
    get_industry_area_id(es)
    get_location_area_id(es)

    concept_area = get_area_data(1)
    print(concept_area)
    for concept in concept_area:
        name, node = concept[u'_id'].split(checkpoint_separator_symbol)
        area_data = get_area_stock_data(node)
        save_area_data_to_es(area_data, name, 1, es)
        save_checkpoint(name, node, 1)


    industry_area = get_area_data(2)
    print(industry_area)
    for industry in industry_area:
        name, node = industry[u'_id'].split(checkpoint_separator_symbol)
        area_data = get_area_stock_data(node)
        save_area_data_to_es(area_data, name, 2, es)
        save_checkpoint(name, node, 2)

    location_area = get_area_data(3)
    print(location_area)
    for location in location_area:
        name, node = location[u'_id'].split(checkpoint_separator_symbol)
        area_data = get_area_stock_data(node)
        save_area_data_to_es(area_data, name, 3, es)
        save_checkpoint(name, node, 3)
    print("catch all stock data finish!")
