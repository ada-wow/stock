
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
    exchanges = []
    current_brokers = os.getcwd() + '\\broker'
    current_glalics = os.getcwd() + '\\garlic'
    current_foreign_invest = os.getcwd() + '\\foreign_invest'
    current_exchange = os.getcwd() + '\\exchange'
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
    with open(current_exchange, 'r') as f:
        exchange = True
        while exchange:
            exchange = f.readline()
            if exchange:
                exchanges.append(exchange.replace('\n',''))

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
    index_name = "institution_2020_08_25"
    es = Elasticsearch(hosts="http://localhost:9200")
    for item in scroll_by_query(es, index_name, body):
        if basic_data.has_key(item['symbol']):
            basic_data[item['symbol']].append(item['holder_name'])
        else:
            basic_data[item['symbol']] = [item['holder_name']]

    result = {}
    for symbol in basic_data.keys():
        holders = basic_data[symbol]
        match_count = 0
        match_broker = False
        match_glalic = False
        match_foreign = False
        match_social = False
        match_private = False
        match_exchange = False
        for holder in holders:
            if (not match_broker) and str(holder) in brokers:
                match_broker = True
            if (not match_glalic) and str(holder) in glalics:
                match_glalic = True
            if (not match_glalic) and str(holder) in foreign_invests:
                match_foreign = True

            if (not match_social) and "社保" in holder:
                match_social = True
            if (not match_private) and "私募" in holder:
                match_private = True
            if (not match_exchange) and str(holder) in exchanges:
                match_exchange = True
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
        if match_exchange: #交易所
            match_count = match_count + 1
        result[symbol] = match_count
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
        if result[key] == 2:
            match_two.append((key, result[key]))
    for item in match_five:
        print(item)
    for item in match_four:
        print(item)
    for item in match_three:
        print(item)
    for item in match_two:
        print(item)






    print("hello")