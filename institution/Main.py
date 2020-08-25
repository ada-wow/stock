
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def get_top_holder(circula, symbol, locate=None, count=5000):
    url = "https://stock.xueqiu.com/v5/stock/f10/cn/top_holders.json"

    querystring = {"symbol":symbol,"circula":circula,"count":count}
    if locate:
        querystring["locate"] = locate

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
'Referer': 'https://xueqiu.com/snowman/S/SZ002797/detail',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Cookie': '_ga=GA1.2.232444739.1549972267; device_id=24700f9f1986800ab4fcc880530dd0ed; s=ce1bjaqtid; xq_a_token=4db837b914fc72624d814986f5b37e2a3d9e9944; xq_r_token=2d6d6cc8e57501dfe571d2881cabc6a5f2542bf8; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTYwMDQ4MzAwNywiY3RtIjoxNTk4MDY2ODIyNjc0LCJjaWQiOiJkOWQwbjRBWnVwIn0.N1705I6ZerltkE5vOzy6vaVkjEpYOUloNInZVopXQPNnBxM2mAD6PUL80OXCigRWK3xwTUt3G4bYpkaPgNcMwDhpG8lnSb4MhOBm8apE1HMEyn1oRE9GNhyMHBCLFj2FFMy9d15POECJggdlTM3z9qGFki4bsHiwKDCKlvOhGAWfynPpbqr8ivsYt0xhHQmwLMe7UZaJsoq32ZqzUy6lygZMV7ykxZs_oOKy8vZfLXeCcvy-UGdtayvOgKwW592Cgc8NpVU5qHDJ0m6AdExAnyCL_XxwqMAX102eVwVUZuALouUqR_R1Ro3X9hj6_HHqIGFLgzvtSedoXcdE2zp7fQ; u=491598066844087; Hm_lvt_1db88642e346389874251b5a1eded6e3=1597833682,1598066844,1598100049,1598102454; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1598364567'
#'Cookie': '_ga=GA1.2.232444739.1549972267; device_id=24700f9f1986800ab4fcc880530dd0ed; s=ce1bjaqtid; xq_a_token=69a6c81b73f854a856169c9aab6cd45348ae1299; xqat=69a6c81b73f854a856169c9aab6cd45348ae1299; xq_r_token=08a169936f6c0c1b6ee5078ea407bb28f28efecf; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTU5ODMyMzAwNCwiY3RtIjoxNTk3MzE5MjQ3NjA4LCJjaWQiOiJkOWQwbjRBWnVwIn0.KpU4uW9yv1jCCMqOYezNAhzbsebfwTe_xzMh-PRnVjS8N7EbgopFvi-lCAuXYi7Sxoap_rfGYnpGwFMlRgG54-xRodw-fLba_BPXikIGM56TG6dcEn1GEviTgUZRaiCH5U3_XDVyhAm_dK5nIamobGNfzcYtN9YCRANPP0Bv8B1owZew6Yr4tTq3uGgcBuSYBRMFpDuoT46VcBknV-yZe1xQUZVW-l-GML-blK1UJMU1gtQpxlxahPrbZAsxxZI0Zto6Go8EVITXpHxMt1skCLcWDVqSZdA65cuT3Wn1m-spVI6GkswhZbYRP-Gm3vn4ymtOIeZE8J1cxHUbgM7OBQ; u=161597319294924; Hm_lvt_1db88642e346389874251b5a1eded6e3=1597319777,1597412476,1597562890,1597756814; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1597759445'

}
    get_xueqiu_succ = False
    while not get_xueqiu_succ:
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            get_xueqiu_succ = True
        except Exception, ex:
            print("get xueqiu error:", ex.message)
            time.sleep(30)
    return response.json()


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
        time.sleep(0.1)
        for i in range(3):
            top_holder_json = get_top_holder(circula, symbol)
            if len(top_holder_json['data']['times']) == 0:
                time.sleep(0.5)
                print(symbol)
            else:
                break
        print(top_holder_json)
        if len(top_holder_json['data']['times']) == 0:
            print("No result")
            continue
        else:
            if int(top_holder_json['data']['times'][0]['value']) < latest_min_time:
                print ("out  date stock")
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
                time.sleep(0.1)
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
                time.sleep(0.1)
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


