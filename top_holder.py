
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
'Cookie': '_ga=GA1.2.232444739.1549972267; device_id=24700f9f1986800ab4fcc880530dd0ed; s=ce1bjaqtid; Hm_lvt_1db88642e346389874251b5a1eded6e3=1597412476,1597562890,1597756814,1597833682; xq_a_token=4db837b914fc72624d814986f5b37e2a3d9e9944; xqat=4db837b914fc72624d814986f5b37e2a3d9e9944; xq_r_token=2d6d6cc8e57501dfe571d2881cabc6a5f2542bf8; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTYwMDQ4MzAwNywiY3RtIjoxNTk3ODk5MjEyOTYyLCJjaWQiOiJkOWQwbjRBWnVwIn0.Ojzrk1dDcRMhFAxApG7dYe7I5hGHQ_bfW6KcOpVxcADiQ_DPyPOq3HbxSuLdSH9-Vfp3SjvWSB6m_ywq_bpB4QvJjUpCkav_MTt9ZsZpGDvmKYw-Df5kcHQ_0UgXc3ORGgOM9oDW7jm7KwYM0fBsT-QGE8k5kp7-EclLDhbNxCuP4dIwBoJkwtyUObhNUsonHhNjtC3FvRkOiuDu1VGJ-GMN3D0KTcQ1ijyqizwHtG4x2OXPYIsnuFoJWHI7SiLIfMQZMegeUUkBXWIZlmIm_CzjZtubDNIk9KH2-RiV-iW-lg4Env4zv3MeCZphK5G6W2Nxl13P1uWghg10G6RzHA; u=471597899254614; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1597930141'
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


def save_top_holder(resp, circula, index_name, es):
    for item in resp[u'hits'][u'hits']:
        item = item['_source']
        symbol = item[u'symbol']
        exist = False
        try:
            symbol_id = symbol + "_" + str(circula)
            stock_doc = es.get("tmp_holder_record", id=symbol_id)
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
                time.sleep(1)
                print(symbol)
            else:
                break
        print(top_holder_json)
        if len(top_holder_json['data']['times']) == 0:
            print("No result")
            continue

        is_latest_one = True
        update_mode_count = 0
        actions = []
        all_report_times = top_holder_json['data']['times']
        for each_report in all_report_times:
            if update_mode and update_mode_count == 2:
                break
            update_mode_count = update_mode_count + 1
            if not is_latest_one:
                top_holder_json = get_top_holder(circula, symbol, each_report['value'])
                time.sleep(0.1)
            seq = 1
            for stud in top_holder_json['data']['items']:
                symbol_id = symbol + "_" + str(each_report['value']) + "_" + str(circula) + "_" + str(seq),
                exist = False
                try:
                    stock_doc = es.get(index_name, id=symbol_id)
                    exist = True
                except Exception as ex:
                    pass
                if exist:
                    break
                action = {
                    "_index": index_name,
                    "_id": symbol + "_" + str(each_report['value']) + "_" + str(circula) + "_" + str(seq),
                    "_source": {
                        "symbol": symbol,
                        "name": item[u'name'],
                        "change": stud['chg'],
                        "held_num": stud['held_num'],
                        "held_ratio": stud['held_ratio'],
                        "holder_name": stud['holder_name'],
                        "circula": circula,
                        "display_date": each_report['value'] / 1000,
                        "latest": 1 if is_latest_one else 0,
                        "update_time": int(time.time())
                    }
                }
                seq = seq + 1
                actions.append(action)
            if is_latest_one:
                is_latest_one = False
        if len(actions) > 0:
            bulk_succ = False
            while not bulk_succ:
                try:
                    helpers.bulk(es, actions)
                    bulk_succ = True
                except Exception:
                    time.sleep(5)
        symbol_id = symbol + "_" + str(circula)
        es.index(index='tmp_holder_record', body={}, id=symbol_id)
        print(item[u'name'].encode('utf-8'))

if __name__ == '__main__':
    index_name = "top_holder"
    update_mode = True
    es = Elasticsearch(hosts="http://localhost:9200")
    body = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    resp = es.search(index="stock_2020-08-20", body=body)

    save_top_holder(resp, 0, index_name, es)
    save_top_holder(resp, 1, index_name, es)


