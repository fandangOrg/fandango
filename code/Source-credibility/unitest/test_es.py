from connectors.elasticsearch_connector import ElasticsearchConnector
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch


es_man = ElasticsearchConnector(host="localhost", port="9220")
es_man.connect()

index = "fdg-article"
search_key = "publisher"
uuid = "7457b5f27a46e69e3f891767d01d2c6f6c5829132a4c03e78f4858828d539fc983a70a3c43ff8a082a8650c0972349eafb50bda7a44062428e2b405249a387f3"

a = "7457b5f27a46e69e3f891767d01d2c6f6c5829132a4c03e78f4858828d539fc983a70a3c43ff8a082a8650c0972349eafb50bda7a44062428e2b405249a387f3"
s = Search(using=es_man.es, index=index).query("match", publisher=uuid)
s = s.query("match", publisher=uuid)
s = s.execute()


multi_match = MultiMatch(query=uuid, fields=['publisher'])

s2 = Search(using=es_man.es, index=index).query(multi_match)
s2 = s2.execute()



art_index = "fdg-textscore"
art_id1 = "8796aff2a14a1ea1539265f76b044f1faf00304d6d9e237aaa21da6c4bab2166f0bed8a2eb99a05d18bc945f811f250da1f4c5a4acbfff1a213bc773894edcd1"
art_id2 = "8796aff2a14a1ea1539265f76b044f1faf00304d6d9e237aaa21da6c4bab2166be47575aa0278fdaaccf0d0aac645381b6db09383e58519fc3589398b63777b3"

sss = Search(using=es_man.es, index=art_index) \
    .filter("terms", _id=[art_id1, art_id2])

response = sss.execute()


# ------------------------------------------
# Get all authors associated to publisher
# ------------------------------------------

multi_match = MultiMatch(query=uuid, fields=['publisher'])

s4 = Search(using=es_man.es, index="fdg-article").query(multi_match)
s4 = s4.execute()
response_dct: dict = s4.to_dict()

authors = [i.get("_source").get("authors") for i in response_dct.get("hits").get("hits")]

import itertools

authors_flatten_uuids = list(set(itertools.chain.from_iterable(authors)))

# retrieve objects
search_query: Search = Search(using=es_man.es, index="fdg-ap-person") \
    .filter("terms", _id=authors_flatten_uuids)

response_auth = search_query.execute().to_dict()

total_authors = len(authors_flatten_uuids)
anonymous = len([i for i in response_auth.get("hits").get("hits") if i.get("_source").get("name") == "Anonymous"])