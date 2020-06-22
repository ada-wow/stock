# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import json
import time
from elasticsearch import Elasticsearch

index_name = "stock-2020-06-22"
date_str = "2020-06-22"
timeArray = time.strptime(date_str, '%Y-%m-%d')
current_time = int(time.mktime(timeArray))

def get_concept_area_id():
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    concept_array = resp.json()[1][0][1][3][1]
    concept_area = []
    for concept in concept_array:
        data = {
            "name": concept[0],
            "node": concept[2]
        }
        concept_area.append(data)
    return concept_area

def get_industry_area_id():
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    industry_array = resp.json()[1][0][1][4][1]
    industry_area = []
    for concept in industry_array:
        data = {
            "name": concept[0],
            "node": concept[2]
        }
        industry_area.append(data)
    return industry_area

def get_location_area_id():
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    resp = requests.get(url)
    location_array = resp.json()[1][0][1][5][1]
    location_area = []
    for concept in location_array:
        data = {
            "name": concept[0],
            "node": concept[2]
        }
        location_area.append(data)
    return location_area

def get_area_data(node):
    area_data = []
    page = 1
    while(True):
        time.sleep(4)
        url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=" + str(page) + "&num=40&sort=symbol&asc=1&node=" + str(node) + "&symbol=&_s_r_a=init"
        #url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=" + str(page) + "&num=40&sort=symbol&asc=1&node=chgn_700682&symbol=&_s_r_a=auto"
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
            stock_doc = es_client.get(index_name, id = stock["symbol"])
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

if __name__ == '__main__':


    es = Elasticsearch(hosts="http://localhost:9200")

    concept_area = get_concept_area_id()
    print(concept_area)
    for concept in concept_area:
        area_data = get_area_data(concept['node'])
        save_area_data_to_es(area_data, concept['name'], 1, es)

    industry_area = get_industry_area_id()
    print(industry_area)
    for industry in industry_area:
        area_data = get_area_data(industry['node'])
        save_area_data_to_es(area_data, industry['name'], 2, es)

    location_area = get_location_area_id()
    print(location_area)
    for location in location_area:
        area_data = get_area_data(location['node'])
        save_area_data_to_es(area_data, location['name'], 3, es)








