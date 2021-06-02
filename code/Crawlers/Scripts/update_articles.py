# from elasticsearch import Elasticsearch
# from elasticsearch import helpers
# from elasticsearch.exceptions import TransportError
# from urllib.parse import urlparse
# from collections import defaultdict
# from datetime import datetime
# import hashlib
# from adblockparser import AdblockRules
#
#
# # settings = {
# #     "settings": {"number_of_shards": 3, "number_of_replicas": 1},
# #     "mappings": {"request": {"properties": {
# #         "identifier": {"type": "keyword"},
# #         "url": {"type": "keyword"},
# #         "timestamp": {"type": "date"},
# #         "priority": {"type": "integer"},
# #         "request": {"type": "binary"},
# #         "visited": {"type": "boolean"},
# #         "scheduled": {"type": "boolean"},
# #         "spider": {"type": "keyword"}
# #     }}}
# # }
# dtype = "article"
# settings = {
#     "settings": {"number_of_shards": 9, "number_of_replicas": 1},
#     "mappings": {dtype: {"properties": {
#         "identifier": {"type": "keyword"},
#         "title": {"type": "text"},
#         "text": {"type": "text"},
#         "images": {"type": "text"},
#         "videos": {"type": "text"},
#         "date_created": {"type": "date"},
#         "date_modified": {"type": "date"},
#         "date_published": {"type": "date"},
#         "publish_date_estimated": {"type": "keyword"},
#         "authors": {"type": "text"},
#         "source_domain": {"type": "keyword"},  # unneeded
#         "summary": {"type": "text"},  # unneeded
#         "description": {"type": "text"},
#         "keywords": {"type": "keyword"},
#         "language": {"type": "keyword"},
#         "top_image": {"type": "text"},  # unneeded
#         "url": {"type": "keyword"},
#         "texthash": {"type": "keyword", "index": False},  # if used with curl replace False with false
#         "fakeness": {"type": "keyword"},
#         "spider": {"type": "keyword"},
#         "linkNumber": {"type": "integer"}
#     }}}
# }
#
#
# source_elastic = Elasticsearch(["83.212.123.15:9200"])
# source_index = "certh-article"
#
# target_elastic = Elasticsearch(["83.212.123.15:9200"])
# target_index = "certh-scheduler"
#
# if not target_elastic.indices.exists(target_index):
#     print(target_elastic.indices.create(target_index, ignore=400, body=settings))
#
#
# res = source_elastic.search(index=source_index, body={
#     'size': 100,
#     'query': {'match_all': {}}
# }, scroll='10m')
# total = res['hits']["total"]
# counter = 0
#
# while len(res['hits']['hits']) > 0:
#     scroll = res['_scroll_id']
#     batch_insert = []
#     batch_delete = []
#     for found in res['hits']['hits']:
#         # process
#         item = found["_source"]
#         url = item["url"]
#         identifier = (hashlib.sha256(".".join(urlparse(url).netloc.split(".")[-2:]).encode('utf-8')).hexdigest() +
#                       hashlib.sha256(urlparse(url).path.encode('utf-8')).hexdigest())
#         item["identifier"] = identifier
#         item["spider"] = "groundtruth"
#
#         if target_elastic.exists(target_index, identifier, ):
#             stored = target_elastic.get(target_index, identifier)["_source"]
#             item["visited"] = any([item["visited"], stored["visited"]])
#             item["scheduled"] = any([item["scheduled"], stored["scheduled"]])
#
#         counter += 1
#
#         batch_insert.append({
#             "_id": identifier,
#             "_index": target_index,
#             "_type": dtype,
#             "_source": item
#         })
#         batch_delete.append({
#             '_op_type': 'delete',
#             '_index': source_index,
#             '_type': dtype,
#             '_id': found["_id"]})
#
#     com_ind = helpers.bulk(target_elastic, batch_insert, chunk_size=1000, request_timeout=200)[0]
#     com_rem = helpers.bulk(source_elastic, batch_delete, chunk_size=1000, request_timeout=200)[0]
#
#     res = source_elastic.scroll(scroll_id=scroll, scroll='10m')
#
#     print("processed", counter, "out of", total)
