from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import TransportError
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime
import hashlib


# settings = {
#     "settings": {"number_of_shards": 3, "number_of_replicas": 1},
#     "mappings": {"request": {"properties": {
#         "identifier": {"type": "keyword"},
#         "url": {"type": "keyword"},
#         "timestamp": {"type": "date"},
#         "priority": {"type": "integer"},
#         "request": {"type": "binary"},
#         "visited": {"type": "boolean"},
#         "scheduled": {"type": "boolean"},
#         "spider": {"type": "keyword"}
#     }}}
# }
dtype = "article"
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


processed = []

source_elastic = Elasticsearch(["83.212.123.15:9200"])
source_index = "certh-article"

res = source_elastic.search(index=source_index, body={
    'size': 1000,
    'query': {'match_all': {}}
}, scroll='10m')
total = res['hits']["total"]
counter = 0

begin = datetime.now()

while len(res['hits']['hits']) > 0:
    start = datetime.now()
    scroll = res['_scroll_id']
    batch_insert = []
    batch_delete = []
    for found in res['hits']['hits']:
        # process
        item = found["_source"]

        if "url" in item.keys():
            url = item["url"]
            identifier = (hashlib.sha256(".".join(urlparse(url).netloc.split(".")[-2:]).encode('utf-8')).hexdigest() +
                          hashlib.sha256(urlparse(url).path.encode('utf-8')).hexdigest())
            batch_delete.append({
                '_op_type': 'update',
                '_index': source_index,
                '_type': dtype,
                '_id': found["_id"],
                '_source': {'doc': {"identifier": identifier}}
            })
            processed.append((found["_id"], identifier))
            counter += 1
    com_rem = helpers.bulk(source_elastic, batch_delete, chunk_size=1000, request_timeout=200)[0]
    res = source_elastic.scroll(scroll_id=scroll, scroll='10m')
    current = datetime.now()
    batch_elapsed = current - start
    total_elapsed = current - begin
    estimated = (total / counter) * total_elapsed
    print(batch_elapsed, counter, "out of", total, "\t\t", "running:", total_elapsed, "estimated total time:", estimated)



