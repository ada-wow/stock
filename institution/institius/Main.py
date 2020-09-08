
# coding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def scroll_by_query(es, index_name, body):
    resp = es.search(body, index_name, doc_type="_doc", params={"scroll": "1m"})

    scroll_id = resp['_scroll_id']
    for item in resp[u'hits'][u'hits']:
        yield item['_source']

    while len(resp[u'hits'][u'hits']) > 0:
        body = {
            "scroll": "1m",
            "scroll_id": scroll_id
        }
        resp = es.scroll(body, scroll_id=scroll_id)
        scroll_id = resp['_scroll_id']
        for item in resp[u'hits'][u'hits']:
            yield item['_source']


if __name__ == '__main__':
    brokers = []
    glalics = []
    foreign_invests = []
    govers = []
    exists = []
    current_brokers = os.getcwd() + '\\broker'
    current_glalics = os.getcwd() + '\\garlic'
    current_foreign_invest = os.getcwd() + '\\foreign_invest'
    current_gover = os.getcwd() + '\\goverment'
    current_exists = os.getcwd() + "\\exists"
    with open(current_exists, 'r') as f:
        exist = True
        while exist:
            exist = f.readline()
            if exist:
                exists.append(exist.replace('\n', ''))
    with open(current_brokers, 'r') as f:
        broker = True
        while broker:
            broker = f.readline()
            if broker:
                brokers.append(broker.replace('\n',''))
    with open(current_glalics, 'r') as f:
        glalic = True
        while glalic:
            glalic = f.readline()
            if glalic:
                glalics.append(glalic.replace('\n',''))

    with open(current_foreign_invest, 'r') as f:
        foreign = True
        while foreign:
            foreign = f.readline()
            if foreign:
                foreign_invests.append(foreign.replace('\n',''))
    with open(current_gover, 'r') as f:
        gover = True
        while gover:
            gover = f.readline()
            if gover:
                govers.append(gover.replace('\n',''))

    for broker in brokers:
        print(broker)
    for glalic in glalics:
        print(glalic)
    basic_data = {}
    body = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    index_name = "institution_2020_08_27"
    es = Elasticsearch(hosts="http://localhost:9200")
    for item in scroll_by_query(es, index_name, body):
        if basic_data.has_key(item['symbol']):
            basic_data[item['symbol']].append(item['holder_name'])
        else:
            basic_data[item['symbol']] = [item['holder_name']]

    result = {}
    hit_result = {}
    for symbol in basic_data.keys():
        holders = basic_data[symbol]
        match_count = 0
        hit_count = 0
        match_broker = False
        match_glalic = False
        match_foreign = False
        match_social = False
        match_private = False
        match_gover = False
        if symbol == "sh688007":
            import pdb;pdb.set_trace()
        for holder in holders:

            if "基金" not in holder and (holder.endswith("证券股份有限公司") or holder.endswith("证券有限责任公司") or holder.endswith("证券有限公司")):
                match_broker = True
                hit_count = hit_count + 1
            if str(holder) in glalics:
                match_glalic = True
                hit_count = hit_count + 1
            if "交易所" in holder or (holder.endswith("自有资金") and "公司" not in holder):
                match_foreign = True
                hit_count = hit_count + 1
            else:
                for foreign in foreign_invests:
                    if foreign in str(holder):
                        match_foreign = True
                        hit_count = hit_count + 1
                        break
            if ("社保" in holder or holder.startswith("基本养老")):
                match_social = True
                hit_count = hit_count + 1
            if "私募" in holder:
                match_private = True
                hit_count = hit_count + 1
            if str(holder) in govers:
                match_gover = True
                hit_count = hit_count + 1
        if match_broker:# 券商
            match_count = match_count + 1
        if match_glalic:# 牛散
            match_count = match_count + 1
        if match_foreign:# 外资
            match_count = match_count + 1
        if match_social: # 社保
            match_count = match_count + 1
        if match_private: # 私募
            match_count = match_count + 1
        if match_gover: # 政府机构
            match_count = match_count + 1
        result[symbol] = match_count
        hit_result[symbol] = hit_count





    match_five = []
    match_four = []
    match_three = []
    match_two = []
    for key in result.keys():
        if result[key] == 5:
            match_five.append((key, result[key]))
        if result[key] == 4:
            match_four.append((key, result[key]))
        if result[key] == 3:
            match_three.append((key, result[key]))
        # if result[key] == 2:
        #     match_two.append((key, result[key]))
    for key,value in match_five:
        if key not in exists:
            print(key, value)
    for ey,value in match_four:
        if key not in exists:
            print(key, value)
    for ey,value in match_three:
        if key not in exists:
            print(key, value)
    # for item in match_two:
    #     print(item)
    print("hello")


    order_result = sorted(hit_result.items(),key = lambda x:x[1],reverse = True)
    for key, value in order_result:
        if value > 3 and result[key] > 2:
            if key not in exists:
                print(key, value)

    print('word')

    order_result = sorted(hit_result.items(), key=lambda x: x[1], reverse=True)
    for key, value in order_result:
        if value > 4:
            if key not in exists:
                print(key, value)


