# transfer all documents from an elastic index to a kafka topic

from elasticsearch import Elasticsearch
# from pykafka import KafkaClient
import json

from collections import Counter


#
# es = Elasticsearch(["10.0.0.5"], port=9220)
# index_current = 'raw_news_articles'
# dtype = 'article'
#
#
# connection = KafkaClient(hosts="10.0.0.4:9092")
# client = connection.topics["test_articles"]
#

# # transfer all in batches of 1000
# query = {
#     'size': 1000,
#     'query': {
#         'match_all': {}
#     }
# }

es = Elasticsearch(["127.0.0.1"], port=9900)
index_current = 'merged_articles'
dtype = 'article'

query = {
    'size': 1000,
    'query': {
        'match': {"language": "lang"}
    }
}

for lang in ["it", "es", "en", "nl"]:
    cnt = 0
    connection = KafkaClient(hosts="83.212.123.15:9992")
    client = connection.topics["articles_%s" % lang]
    query["query"]["match"]["language"] = lang
    with client.get_sync_producer() as kafka:
        res = es.search(index=index_current, doc_type=dtype, body=query, scroll='5m')
        while len(res['hits']['hits']) > 0:
            scroll = res['_scroll_id']
            for article in res['hits']['hits']:
                cnt += 1
                p = kafka.produce(json.dumps(article['_source']))
                print(lang, "%08d" % cnt)
            res = es.scroll(scroll_id=scroll, scroll='5m')


# ######################### check if data were moved ###################################
# from pykafka import KafkaClient
# import json
#
# connection = KafkaClient(hosts="10.0.0.4:9092")
# client = connection.topics["test_articles"]
#
#
# articles = []
# consumer = client.get_simple_consumer()
#
# for message in consumer:
#     if message is not None:
#         article = json.loads(message.value)
#         articles.append(article)
#         print message.offset, article["text"]
#


# ############# transfer a sample to kafka (for david) ##################
# from elasticsearch import Elasticsearch
# from pykafka import KafkaClient
# import json
#
#
# es = Elasticsearch(['10.0.0.5'], port=9220)
# index_current = 'news_article_current'
# dtype = 'article'
#
#
# connection = KafkaClient(hosts="10.0.0.4:9092")
# client = connection.topics["test_articles"]
#
# query = {
#     'size': 5000,
#     'query': {
#         'match_all': {}
#     }
# }
#
# with client.get_sync_producer() as kafka:
#     res = es.search(index=index_current, doc_type=dtype, body=query)
#     for article in res['hits']['hits']:
#         kafka.produce(json.dumps(article['_source']))
#


# ############### create a balanced sample for topic and entity extraction ################
#
# es = Elasticsearch(["10.0.0.5"], port=9220)
# index_current = 'raw_news_articles'
# dtype = 'article'
#
#
# connection = KafkaClient(hosts="10.0.0.4:9092")
# client = connection.topics["balanced_sample"]
#
# articles = []
# query = {
#     'size': 1000,
#     'query': {
#         'match': {'fakeness': 'bad'}
#     }
# }
# bad = es.search(index=index_current, doc_type=dtype, body=query)
# for article in bad['hits']['hits']:
#     if json.loads(article['_source'])["text"]:
#         articles.append(article['_source'])
#
# query = {
#     'size': 1000,
#     'query': {
#         'match': {'fakeness': 'good'}
#     }
# }
# good = es.search(index=index_current, doc_type=dtype, body=query)
# for article in good['hits']['hits']:
#     if json.loads(article['_source'])["text"]:
#         articles.append(article['_source'])
#
#
# with client.get_sync_producer() as kafka:
#     for article in articles:
#         kafka.produce(json.dumps(article))
#

# ############### create a balanced sample (for david) ################
#
# from elasticsearch import Elasticsearch
# from pykafka import KafkaClient
# from collections import Counter
# import json
#
#
# es = Elasticsearch(['83.212.123.15'], port=9200)
# index_current = 'news_article_current'
# dtype = 'article'
#
#
# connection = KafkaClient(hosts="10.0.0.4:9092")
# client = connection.topics["test_articles"]
#
#
# query = {
#     'size': 1000,
#     'query': {
#         'match_all': {}
#     }
# }
#
# cnt = 0
# scn = 0
# language_counter = Counter()
# language_counter[""] = 2000
# domain_counter = Counter()
# domain_counter[""] = 300
#
#
# with client.get_sync_producer() as kafka:
#     res = es.search(index=index_current, doc_type=dtype, body=query, scroll='15m')
#     while (len(res['hits']['hits']) > 0) and (cnt <= 5000):
#         scroll = res['_scroll_id']
#         for article in res['hits']['hits']:
#             scn += 1
#             lang = article['_source'].get('language', "")
#             domain = article['_source'].get('source_domain', "")
#             if (language_counter[lang] < 1500) and (domain_counter[domain] < 200):
#                 p = kafka.produce(json.dumps(article['_source']))
#                 language_counter[lang] += 1
#                 domain_counter[domain] += 1
#                 cnt += 1
#             print "scanned", scn, "added", cnt, "lang", lang, "domain", domain
#         res = es.scroll(scroll_id=scroll, scroll='15m')
#
#
# print "per language", language_counter.most_common()
# print "per domain", domain_counter.most_common()
#

from elasticsearch import Elasticsearch as Elasticsearch6
from elasticsearch5 import Elasticsearch as Elasticsearch5


query = {
    'size': 1000,
    'query': {
        'match_all': {}
    }
}

es = Elasticsearch(["83.212.123.15"], port=9200)

ids = []

res = es.search(index="vittoriano", doc_type="article", body=query, scroll='3m')
while len(res["hits"]["hits"]) > 0:
    print(len(res["hits"]["hits"]))
    scroll = res['_scroll_id']
    for result in res["hits"]["hits"]:
        ids.append(result["_id"])
        # es.delete(index="vittoriano", doc_type="article", id=result["_id"])
    res = es.scroll(scroll_id=scroll, scroll='3m')

for result in ids:
    es.delete(index="vittoriano", doc_type="article", id=result)

