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

def echo_kibana_query(name_set):
    if not name_set:
        return ""
    query = ""
    seq = 1
    for name in name_set:
        name = name.replace("(", "\(")
        name = name.replace(")", "\)")
        if seq == 1:
            query = "holder_name.keyword:" + name
        else:
            query = query + " OR " + "holder_name.keyword:" + name
        seq = seq + 1

    return query