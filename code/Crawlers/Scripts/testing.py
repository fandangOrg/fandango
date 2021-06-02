from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from collections import defaultdict
import hashlib
# import json

source_elastic = Elasticsearch(["83.212.120.20"], port=9900)
# source_elastic = Elasticsearch(["127.0.0.1"], port=9900)
# source_index = "raw_claim_reviews_data"
source_index = "clean_claims"

# target_elastic = Elasticsearch(["83.212.120.20"], port=9900)
target_elastic = Elasticsearch(["127.0.0.1"], port=9900)
target_index = "clean_claims"

dtype = 'crawledClaim'

# transfer all in batches of 1000
query = {
    'size': 1000,
    'query': {
        'match_all': {}
    }
}


bloomberg = defaultdict(set)
illegal = [u"\xab", u"\xbb"]


res = target_elastic.search(index=target_index, doc_type=dtype, body=query, scroll='5m')
while len(res['hits']['hits']) > 0:
    scroll = res['_scroll_id']
    for claim in res['hits']['hits']:
        url = claim['_source'].get("url", "")
        topic = claim['_source'].get("claimReview", dict()).get("claimReviewed", "")
        for ch in illegal:
            topic = topic.replace(ch, "")
        texthash = hashlib.sha256(topic.encode('utf-8')).hexdigest()
        bloomberg[url].add(texthash)
    res = target_elastic.scroll(scroll_id=scroll, scroll='5m')


res = source_elastic.search(index=source_index, doc_type=dtype, body=query, scroll='5m')
while len(res['hits']['hits']) > 0:
    scroll = res['_scroll_id']
    for claim in res['hits']['hits']:
        topic = claim['_source'].get("claimReview", dict()).get("claimReviewed", "")
        if topic:
            url = claim['_source'].get("url", "")
            for ch in illegal:
                topic = topic.replace(ch, "")
            texthash = hashlib.sha256(topic.encode('utf-8')).hexdigest()
            if texthash not in bloomberg[url]:
                bloomberg[url].add(texthash)
                claim_source = claim['_source']
                try:
                    target_elastic.index(index=target_index, doc_type='crawledClaim', body=claim_source)
                except RequestError:
                    claim_source['claimReview']['author']['logo'] = {"url": claim_source['claimReview']['author']['logo']}
                    resp = target_elastic.index(index=target_index, doc_type='crawledClaim', body=claim_source)
    res = source_elastic.scroll(scroll_id=scroll, scroll='5m')




#
# try:
#
# except UnicodeEncodeError:
#     texthash = hashlib.sha256((url + topic[1:-1]).encode('utf-8')).hexdigest()
#
