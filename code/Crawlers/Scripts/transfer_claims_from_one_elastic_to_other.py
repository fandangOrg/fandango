import elasticsearch
from datetime import datetime
import requests
import hashlib

# from scrapy.exceptions import DropItem
# from kafka import KafkaProducer
# from dateutil import parser
# from .fact import Fact
# import logging
# import json
# import sys


local_elastic = elasticsearch.Elasticsearch(['83.212.123.15:9200'])
remot_elastic = elasticsearch.Elasticsearch(['40.114.234.51:9220'])
claims_index = "fdg-claim"
review_index = "fdg-claim-review"
#
# res = local_elastic.search(index=claims_index, body={
#     'size': 100,
#     'query': {'match_all': {}}
# }, scroll='10m')
# total = res['hits']["total"]
# counter = 0
#
#
# while len(res['hits']['hits']) > 0:
#     scroll = res['_scroll_id']
#     for found in res['hits']['hits']:
#         counter += 1
#         claim = found["_source"]
#         identifier = claim.get("identifier")
#         remot_elastic.index(claims_index, claim, "doc", identifier)
#         print("inserted %04d/%04d" % (counter, total))
#     res = local_elastic.scroll(scroll_id=scroll, scroll='10m')
#
#

res = local_elastic.search(index=review_index, body={
    'size': 100,
    'query': {'match_all': {}}
}, scroll='10m')
total = res['hits']["total"]
counter = 0

store = list()
while len(res['hits']['hits']) > 0:
    scroll = res['_scroll_id']
    for found in res['hits']['hits']:
        counter += 1
        claim = found["_source"]
        identifier = claim.get("identifier")
        try:
            remot_elastic.index(review_index, claim, "doc", identifier)
        except elasticsearch.exceptions.RequestError:
            store.append(claim)
            print("failed %d" % len(store))
        print("inserted %04d/%04d" % (counter, total))
    res = local_elastic.scroll(scroll_id=scroll, scroll='10m')

import newspaper
cnn = newspaper.build("https://www.nieuwsblad.be/nieuws/binnenland")
