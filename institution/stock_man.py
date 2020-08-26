
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers





if __name__ == '__main__':
    index_name = "institution_2020_08_25"
    es = Elasticsearch(hosts="http://localhost:9200")
    body = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    instis = set()
    resp = es.search(body, index_name, doc_type="_doc", params={"scroll": "1m"})

    scroll_id = resp['_scroll_id']
    for item in resp[u'hits'][u'hits']:
        holder_name = item['_source']['holder_name']
        if "证券股份" in holder_name and '基金' not in holder_name and "客户" not in holder_name and "账户" not in holder_name:
            instis.add(holder_name)
    while len(resp[u'hits'][u'hits']) >0:
        body = {
            "scroll": "1m",
            "scroll_id": scroll_id
        }
        resp = es.scroll(body, scroll_id=scroll_id)
        scroll_id  = resp['_scroll_id']
        for item in resp[u'hits'][u'hits']:
            holder_name = item['_source']['holder_name']
            if "证券公司" in holder_name and '基金' not in holder_name and "客户" not in holder_name  and "账户" not in holder_name:
                instis.add(holder_name)

    for insti in instis:
        print insti

    query = ""
    seq = 1
    for ins in instis:
        if seq == 1:
            query = "holder_name.keyword:" + ins
        else:
            query = query + " OR " + "holder_name.keyword:" + ins
        seq = seq + 1

    print(query)
    es.clear_scroll(scroll_id=scroll_id)