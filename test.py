# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers




es = Elasticsearch(hosts="http://localhost:9200")
stock_doc = es.get("top_holder", id="sfdad")

print("ada")