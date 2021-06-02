from elasticsearch import Elasticsearch

es = Elasticsearch(['160.40.51.38'], port=9900)
index_current = 'fact_opensources_com'

res = es.search(index=index_current,
                body={"query": {"exists": {"field": "videos"}}})

for doc in res['hits']['hits']:
    video_url = doc["_source"]["videos"][0]
    text = doc["_source"]["text"]

