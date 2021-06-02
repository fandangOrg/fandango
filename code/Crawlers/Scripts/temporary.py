# from elasticsearch import Elasticsearch, TransportError, helpers
# # from elasticsearch5 import Elasticsearch, TransportError, helpers
# from datetime import datetime
#
#
# dtype = 'article'
#
# query = {
#     'size': 1000,
#     'query': {
#         'match_all': {}
#     }
# }
#
#
# source_es = Elasticsearch(['83.212.123.15'], port=9200)
# # source_in = 'merged_articles'
# # target_in = 'vittoriano'
#
#
# # # source_es = Elasticsearch(['127.0.0.1'], port=9900)
# source_in = 'vittoriano'
# #
# # # target_es = Elasticsearch(['83.212.123.15'], port=9200)
# target_in = 'merged_articles'
#
#
# start = datetime.now()
# existing = set()
#
# res = source_es.search(index=target_in, doc_type=dtype, body=query, scroll='10m')
# total = res["hits"]["total"]
# current = 0
# while len(res['hits']['hits']) > 0:
#     scroll = res['_scroll_id']
#     for article in res['hits']['hits']:
#         current += 1
#         url = article['_source']["url"]
#         existing.add(url)
#     res = source_es.scroll(scroll_id=scroll, scroll='10m')
#     print "completed", current, "of", total, "in", datetime.now()-start
#
#
# moved = set()
# query = {
#     'size': 100,
#     'query': {
#         'match_all': {}
#     }
# }
#
# counter = 0
# common = 0
# res = source_es.search(index=source_in, doc_type=dtype, body=query, scroll='1m')
# total = (res["hits"]["total"] // 100) + 1
# print "total possible articles to move", total
# while len(res['hits']['hits']) > 0:
#     scroll = res['_scroll_id']
#     valid_documents = []
#     remove = []
#     counter += 1
#     for article in res['hits']['hits']:
#         url = article['_source']["url"]
#         domain = article['_source']["source_domain"]
#         if url not in (existing | moved):
#             print ".",
#             doc = {
#                 "_id": article['_id'],
#                 "_index": target_in,
#                 "_type": dtype,
#                 "_source": article['_source']
#             }
#             valid_documents.append(doc)
#             remove.append({
#                 '_op_type': 'delete',
#                 '_index': source_in,
#                 '_type': dtype,
#                 '_id': article["_id"]})
#             moved.add(url)
#         else:
#             print "#",
#             common += 1
#     # end = datetime.now()
#     if len(valid_documents) > 0:
#         try:
#             com_ind = helpers.bulk(source_es, valid_documents, chunk_size=1000, request_timeout=200)
#             com_rem = helpers.bulk(source_es, remove, chunk_size=1000, request_timeout=200)
#         except TransportError:
#             com_ind = 0
#             com_rem = 0
#             for article in valid_documents[1:]:
#                 r = source_es.index(target_in, dtype, article["_source"])
#                 if r["result"] == "created":
#                     com_ind += 1
#                 r = source_es.delete(source_in, dtype, article["_id"])
#                 if r["result"] == 'deleted':
#                     com_rem += 1
#         print("indexed", com_ind, "and removed", com_rem, "in batch", counter, "of", total, "common", common)
#     else:
#         print("no valid documents in batch", counter)
#     res = source_es.scroll(scroll_id=scroll, scroll='1m')
#
#
# # {art["_source"]["url"] for art in valid_documents}
#
#
#####################################################################################################################


from elasticsearch import Elasticsearch, TransportError, helpers
# from elasticsearch5 import Elasticsearch, TransportError, helpers
from datetime import datetime


dtype = 'crawledClaim'

query = {
    'size': 100,
    'query': {
        'match_all': {}
    }
}


# source_es = Elasticsearch(['83.212.123.15'], port=9200)
# # source_in = 'merged_articles'
# # target_in = 'vittoriano'

source_es = Elasticsearch(['83.212.123.15'], port=9200)
source_in = 'fdg-claim-review'

target_es = Elasticsearch(['10.0.0.5'], port=9220)
target_in = 'fdg-claim-review'


start = datetime.now()

res = source_es.search(index=source_in, doc_type="doc", body=query, scroll='10m')
total = res["hits"]["total"]
current = 0
while len(res['hits']['hits']) > 0:
    scroll = res['_scroll_id']
    for review in res['hits']['hits']:
        current += 1
        target_es.index(index=target_in, body=review["_source"], id=review["_id"])
    res = source_es.scroll(scroll_id=scroll, scroll='10m')
    print "completed", current, "of", total, "in", datetime.now()-start






#####################################################################################################################


from elasticsearch import Elasticsearch
from urlparse import urlparse
from elasticsearch import helpers
import json
import hashlib
from datetime import datetime, timedelta


source = 'clean_articles'
target = "groundtruth"
dtype = 'article'
es = Elasticsearch(['83.212.123.15'], port=9200)

query = {
    'size': 10,
    'query': {
        'match_all': {}
    }
}

res = es.search(index=source, doc_type=dtype, body=query, scroll='10m')
counter = 0
while len(res['hits']['hits']) > 0:
    scroll = res['_scroll_id']
    for article in res['hits']['hits']:
        body = article["_source"]
        created = datetime.strptime(article["_source"]["date_created"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)
        modified = datetime.strptime(article["_source"]["date_modified"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)
        published = datetime.strptime(article["_source"]["date_published"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)
        body["date_created"] = created.strftime("%Y-%m-%dT%H:%M:%SZ")
        body["date_modified"] = modified.strftime("%Y-%m-%dT%H:%M:%SZ")
        body["date_published"] = published.strftime("%Y-%m-%dT%H:%M:%SZ") if created - published < timedelta(seconds=1) else None
        es.delete(index=source, doc_type=dtype, id=article["_id"])
        es.index(index=target, doc_type=dtype, id=article["_id"], body=body)
    res = es.scroll(scroll_id=scroll, scroll='10m')

###################################################################


import urllib

url = "http://www.corrieriedellasera.it/napoli-apertura-nuova-indagine-sulla-juve-il-pmfaremo-cadere-il-sistema/"
print urllib.urlopen(url).info().getdate('last-modified')





