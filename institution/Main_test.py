

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
            first_time = 0
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




def save_top_holder():
    circula = 1
    all_circula = 0
    latest_min_time = int((time.time() - 200*24*60*60)*1000)
    latest_time = latest_min_time
    process_count = 0
    for i in range(1):
        item =  {
                "symbol": "sh688981",
                "name": u"xx",
                "percent": -7.067,
                "body": {"sell": "77.060", "volume": 219471588, "code": "688981", "name": "\u4e2d\u82af\u56fd\u9645", "nmc": 8016021.804438, "turnoverratio": 21.09835, "ticktime": "15:29:59", "symbol": "sh688981", "pricechange": "-5.860", "changepercent": "-7.067", "trade": "77.060", "high": "84.900", "amount": 17388147968, "buy": "77.050", "low": "75.000", "settlement": "82.920", "open": "79.000", "pb": 8.874, "mktcap": 57143652.993158, "per": 0},
            }
        process_count = process_count + 1
        print("process count: ", process_count)
        symbol = item[u'symbol']
        try:
            price = float(item[u'body'].get("trade", ""))
            if not price:
                print("no price")
                print(item[u'name'].encode('utf-8'))
                continue
        except Exception, ex:
            print("no price in exception")
            print(item[u'name'].encode('utf-8'))
            continue
        # exist = False
        # try:
        #     stock_doc = es.get("tmp_holder_record", id=symbol)
        #     exist = True
        # except Exception as ex:
        #     pass
        # if exist:
        #     print(item[u'name'].encode('utf-8'))
        #     print("exits in temp holder recoerd")
        #     continue
        for i in range(3):
            top_holder_json = get_top_holder(circula, symbol)
            if len(top_holder_json['data']['times']) == 0:
                time.sleep(0.2)
                print(symbol)
            else:
                break
        print(top_holder_json)
        circula_holder = {}
        if len(top_holder_json['data']['times']) == 0:
            print("No circula result")
            #es.index(index='tmp_holder_record', body={}, id=symbol)
            #continue
        else:
            if int(top_holder_json['data']['times'][0]['value']) < latest_min_time:
                print ("out  date stock in circula")
                # import pdb;pdb.set_trace()
                print(item[u'name'].encode('utf-8'))
            else:
                latest_time = top_holder_json['data']['times'][0]['value']


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



        non_circula_holder = {}
        all_circula_holder = {}
        for i in range(3):
            top_holder_json = get_top_holder(all_circula, symbol)
            if len(top_holder_json['data']['times']) == 0:
                time.sleep(0.2)
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
            if len(non_circula_holder) == 10:
                break
            if not is_latest_one:
                top_holder_json = get_top_holder(all_circula, symbol, each_report['value'])
                time.sleep(0.2)
            for stud in top_holder_json['data']['items']:
                single_holder = {
                    "_index": "index_name",
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
            for item in actions:
                print(item)
        print(item[u'name'].encode('utf-8'))


save_top_holder()