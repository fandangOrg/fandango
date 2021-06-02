from elasticsearch import Elasticsearch

# connect to elasticsearch
es = Elasticsearch(['127.0.0.1'], http_auth=('elastic', 'XEPfUca9VU'), port=9200)
# these are the indices that we will use
index_current = 'fake_opensources_com_current'
archive_index = 'fake_opensources_com_archive'

proper_urls = set()
urls_in_es = set()

# open the csv file that contains the urls
with open("csv/proper_urls_from_opensources.csv", 'r') as src:
    for line in src:
        # each line has a url and a type of fakeness
        url, tpe = line.split(",")
        proper_urls.add((url, tpe.strip()))
        # query elasticsearch to look for existing entries from each url
        res = es.search(index=index_current,
                        body={"query": {"match": {'source_domain': url}}})
        # add all hits from the query to a set (no duplicates)
        for doc in res['hits']['hits']:
            urls_in_es.add((doc['_source']['source_domain'], doc['_source']['fakeness'].strip()))
            # print('Found %s' % (doc['_source']['source_domain']))
print(len(proper_urls))
print(len(urls_in_es))

# urls that don't appear in elasticsearch
urls_not_in_es = proper_urls.difference(urls_in_es)

print(len(urls_not_in_es))

with open("urls_to_check_for_status_codes.csv", "a") as cl:
    for url, tpe in urls_not_in_es:
        cl.write(url + ',' + tpe + '\n')





from elasticsearch import Elasticsearch
import json


es = Elasticsearch(['160.40.51.38'], port=9900)

body = {
    'size': 10000,
    'query': {
        'match_all': {}
    }
}

with open("tmp/all_elastic_data.json", "w") as out:
    for index in es.indices.get('*'):
        if index != ".kibana":
            counter = 0
            done = False
            batch = es.search(index=index, body=body, scroll='1m')
            while len(batch['hits']['hits']) != 0:
                for doc in batch['hits']['hits']:
                    counter += 1
                    out.write(json.dumps(doc["_source"]) + "\n")
                    print(index, counter)
                scrl_id = batch['_scroll_id']
                batch = es.scroll(scroll_id=scrl_id, scroll='1m')

