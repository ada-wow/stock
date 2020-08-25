
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def get_top_holder(circula, symbol, locate=None, count=200):
    url = "https://stock.xueqiu.com/v5/stock/f10/cn/top_holders.json"

    querystring = {"symbol":symbol,"circula":circula}
    if locate:
        querystring["locate"] = locate
        querystring["start"] = locate
    else:
        querystring["count"] = count
    current_second_time = int(time.time())
    headers = {
'Host': 'stock.xueqiu.com',
'Connection': 'keep-alive',
'Pragma': 'no-cache',
'Cache-Control': 'no-cache',
'Accept': 'application/json, text/plain, */*',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
'Origin': 'https://xueqiu.com',
'Sec-Fetch-Site': 'same-site',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Dest': 'empty',
'Referer': 'https://xueqiu.com/snowman/S/' + symbol + '/detail',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Cookie': 'xq_a_token=4db837b914fc72624d814986f5b37e2a3d9e9944;'

}
    get_xueqiu_succ = False
    while not get_xueqiu_succ:
        try:
            resp = {}
            response = requests.request("GET", url, headers=headers, params=querystring)
            # if int(response.json()['data']['times'][0]['value']) < int((time.time() - 200 * 24 * 60 * 60) * 1000):
            #     print ("out  date stock")
            #     import pdb;
            #     pdb.set_trace()
            print(querystring)
            print("old:" , response.json()['data']['times'])
            if len(response.json()['data']['times']) > 0:
                first_time = response.json()['data']['times'][0]['value']
                resp = response
            response = requests.request("GET", url, headers=headers, params=querystring)
            if len(response.json()['data']['times']) > 0 and response.json()['data']['times'][0]['value'] > first_time:
                first_time = response.json()['data']['times'][0]['value']
                resp = response
            print("new:" , response.json()['data']['times'])
            response = requests.request("GET", url, headers=headers, params=querystring)
            if len(response.json()['data']['times']) > 0 and response.json()['data']['times'][0]['value'] > first_time:
                first_time = response.json()['data']['times'][0]['value']
                resp = response
            print("lat:", response.json()['data']['times'])
            get_xueqiu_succ = True
        except Exception, ex:
            print("get xueqiu error:", ex.message)
            time.sleep(30)
    resp = resp.json() if resp else {'data':{'times':[]}}
    print("ret:", resp['data']['times'])
    return resp


def save_top_holder(resp, index_name, es):
    circula = 1
    all_circula = 0
    latest_min_time = int((time.time() - 200*24*60*60)*1000)
    process_count = 0
    for item in resp[u'hits'][u'hits']:
        process_count = process_count + 1
        print("process count: ", process_count)
        item = item['_source']
        symbol = item[u'symbol']
        try:
            price = float(json.loads(item[u'body']).get("trade", ""))
            if not price:
                print("no price")
                print(item[u'name'].encode('utf-8'))
                continue
        except Exception, ex:
            print("no price in exception")
            print(item[u'name'].encode('utf-8'))
            continue
        exist = False
        try:
            stock_doc = es.get("tmp_holder_record", id=symbol)
            exist = True
        except Exception as ex:
            pass
        if exist:
            print(item[u'name'].encode('utf-8'))
            print("exits in temp holder recoerd")
            continue
        time.sleep(3)
        for i in range(3):
            top_holder_json = get_top_holder(circula, symbol)
            if len(top_holder_json['data']['times']) == 0:
                time.sleep(3)
                print(symbol)
            else:
                break
        print(top_holder_json)
        if len(top_holder_json['data']['times']) == 0:
            print("No result")
            es.index(index='tmp_holder_record', body={}, id=symbol)
            continue
        else:
            if int(top_holder_json['data']['times'][0]['value']) < latest_min_time:
                print ("out  date stock")
                # import pdb;pdb.set_trace()
                print(item[u'name'].encode('utf-8'))
                continue
        latest_time = top_holder_json['data']['times'][0]['value']
        circula_holder = {}
        non_circula_holder = {}
        all_circula_holder = {}
        for stud in top_holder_json['data']['items']:
            single_holder = {
                "_index": index_name,
                "_id": symbol + "_" + str(hash(stud['holder_name'])),
                "_source": {
                    "symbol": symbol,
                    "name": item[u'name'],
                    "change": stud['chg'],
                    "held_num": stud['held_num'],
                    "held_ratio": stud['held_ratio'],
                    "price": price,
                    "market_value": (stud['held_num'] * price) / 100000000,
                    "holder_name": stud['holder_name'],
                    "display_date": latest_time / 1000
                }
            }
            circula_holder[str(hash(stud['holder_name']))] = single_holder




        while True:
            top_holder_json = get_top_holder(all_circula, symbol)
            if len(top_holder_json['data']['times']) == 0:
                time.sleep(3)
                print("do not get the all_circula holder")
                print(symbol)
            else:
                break
        print(top_holder_json)
        is_latest_one = True
        all_report_times = top_holder_json['data']['times']
        for each_report in all_report_times:
            if each_report['value'] < latest_time:
                break
            if not is_latest_one:
                top_holder_json = get_top_holder(all_circula, symbol, each_report['value'])
                time.sleep(3)
            for stud in top_holder_json['data']['items']:
                single_holder = {
                    "_index": index_name,
                    "_id": symbol + "_" + str(hash(stud['holder_name'])),
                    "_source": {
                        "symbol": symbol,
                        "name": item[u'name'],
                        "change": stud['chg'],
                        "held_num": stud['held_num'],
                        "held_ratio": stud['held_ratio'],
                        "price": price,
                        "market_value": (stud['held_num'] * price) / 100000000,
                        "holder_name": stud['holder_name'],
                        "display_date": each_report['value'] / 1000
                    }
                }
                if not non_circula_holder.has_key(str(hash(stud['holder_name']))):
                    non_circula_holder[str(hash(stud['holder_name']))] = single_holder
            if is_latest_one:
                is_latest_one = False
        for circula_holder_key in non_circula_holder.keys():
            if not all_circula_holder.has_key(circula_holder_key):
                all_circula_holder[circula_holder_key] = non_circula_holder[circula_holder_key]
        for circula_holder_key in circula_holder.keys():
            if not all_circula_holder.has_key(circula_holder_key):
                all_circula_holder[circula_holder_key] = circula_holder[circula_holder_key]
        actions = all_circula_holder.values()
        if len(actions) > 0:
            bulk_succ = False
            while not bulk_succ:
                try:
                    helpers.bulk(es, actions)
                    bulk_succ = True
                except Exception:
                    time.sleep(5)
        es.index(index='tmp_holder_record', body={}, id=symbol)
        print(item[u'name'].encode('utf-8'))

if __name__ == '__main__':
    index_name = "institution_2020_08_25"
    es = Elasticsearch(hosts="http://localhost:9200")
    body = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    resp = es.search(index="stock_2020-08-25", body=body)

    save_top_holder(resp, index_name, es)


