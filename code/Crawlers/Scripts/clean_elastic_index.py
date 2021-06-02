from elasticsearch import Elasticsearch
from urllib.parse import urlparse
from elasticsearch import helpers
import hashlib

# from datetime import datetime, timedelta
# from urlparse import urlparse
# import json


# source = 'vittoriano'
source = 'merged_articles'

target = 'clean_articles'

dtype = 'article'
es = Elasticsearch(['83.212.123.15'], port=9200)

# # transfer all
# domain = urlparse("https://www.ansa.it/web/notizie/rubriche/calcio/statsdir/player/52/player_754079.html").netloc
# query = {
#     'size': 1000,
#     'query': {
#         'match_all': {}
#     }
# }

desired = [
    ("http://www.ansa.it/", "good", "it"),
    ("https://www.repubblica.it/", "good", "it"),
    ("https://www.corriere.it/", "good", "it"),
    ("https://www.ilsole24ore.com/", "good", "it"),
    ("https://www.rainews.it/", "good", "it"),

    ("http://www.il-giornale.info/", "bad", "it"),
    ("https://www.tg24-ore.com/", "bad", "it"),
    ("https://tg-news24.com/", "bad", "it"),
    ("http://il-quotidiano.info/", "bad", "it"),
    ("https://www.lavocedelpatriota.it/", "bad", "it"),
    ("https://www.semplicipensieri.it/", "bad", "it"),

    ("http://attivonews.com/", "bad", "it"),
    ("https://ilsapereepotere2.blogspot.com/", "bad", "it"),

    ("http://www.ilgiornale.it/", "unk", "it"),
    ("https://www.liberoquotidiano.it/", "unk", "it"),
    ("https://www.ilfattoquotidiano.it/", "unk", "it"),

    ("http://elpais.com", "good", "es"),
    ("http://elmundo.es", "good", "es"),
    ("http://elconfidencial.com", "good", "es"),
    ("http://www.rtve.es/noticias/", "good", "es"),
    ("https://cadenaser.com", "good", "es"),

    ("http://diariodenavarra.es", "good", "es"),
    ("https://www.eldiariomontanes.es", "good", "es"),
    ("http://elnortedecastilla.es", "good", "es"),
    ("http://laverdad.es", "good", "es"),

    ("https://www.mediterraneodigital.com", "bad", "es"),
    ("https://casoaislado.com", "bad", "es"),
    ("http://www.elespiadigital.com", "bad", "es"),
    ("http://www.alertadigital.com", "bad", "es"),
    ("http://latribunadecartagena.com/", "bad", "es"),

    ("https://www.vrt.be/vrtnws/nl", "good", "nl"),
    ("http://www.standaard.be", "good", "nl"),
    ("https://www.demorgen.be", "good", "nl"),
    ("https://www.tijd.be", "good", "nl"),
    ("https://nos.nl/nieuws", "good", "nl"),
    ("https://www.volkskrant.nl", "good", "nl"),
    ("https://www.trouw.nl", "good", "nl"),
    ("https://www.nrc.nl", "good", "nl"),

    ("https://www.ninefornews.nl", "bad", "nl"),
    ("https://www.dagelijksestandaard.nl", "bad", "nl"),
    ("https://fenixx.org", "bad", "nl"),
    ("https://jdreport.com", "bad", "nl"),
    ("https://revolutionaironline.com", "bad", "nl"),
    ("https://www.wanttoknow.nl", "bad", "nl"),
    ("https://www.xandernieuws.net", "bad", "nl"),
    ("https://sceptr.net", "bad", "nl"),
    ("https://www.climategate.nl", "bad", "nl"),
    ("https://tpo.nl", "bad", "nl"),

    ("https://www.apnews.com/", "good", "en"),
    ("https://www.washingtonpost.com/", "good", "en"),
    ("https://www.wsj.com/", "good", "en"),
    ("https://www.theguardian.com/", "good", "en"),
    ("https://www.reuters.com", "good", "en"),

    ("https://russia-insider.com/en/", "bad", "en"),
    ("http://en.news-front.info/", "bad", "en"),
    ("https://www.express.co.uk/news/politics", "bad", "en"),
    ("https://www.infowars.com/", "bad", "en"),
    ("https://sputniknews.com", "bad", "en"),

    ("http://www.ilgiornale.it/", "unk", "it"),
    ("https://www.liberoquotidiano.it/", "unk", "it"),
    ("https://www.ilfattoquotidiano.it/", "unk", "it"),
    ("https://www.larazon.es/", "unk", "es"),
    ("https://www.lavanguardia.com/", "unk", "es"),
    ("https://www.eldiario.es/", "unk", "es"),
    ("https://www.elespanol.com/", "unk", "es"),
    ("https://www.thesun.co.uk/", "unk", "en"),                 # change label
    ("https://www.dailymail.co.uk/", "unk", "en"),              # change label
    ("http://www.breitbart.com/", "unk", "en"),                 # change label

]

# existing = set()

for domain, label, lang in desired:
    query = {
        'size': 10,
        'query': {
            'match': {'source_domain': urlparse(domain).netloc}
        }
    }
    res = es.search(index=source, body=query, scroll='10m')
    counter = 0
    while len(res['hits']['hits']) > 0:
        scroll = res['_scroll_id']
        process = []
        backup = []
        remove = []
        counter += 1
        for article in res['hits']['hits']:
            # if article['_source']['language'] != lang:
            #     print(article['_source']['url'])
            if article['_source']['language'] in ["", "unk"]:
                article['_source']['language'] = lang
            article['_source']['fakeness'] = label

            url_key = hashlib.sha256(article['_source']['url'].encode("utf-8")).hexdigest()
            # dom_key = hashlib.sha256(article['_source']['source_domain'].encode("utf-8")).hexdigest()
            # key = url_key[:32] + dom_key + url_key[32:]

            if not es.exists(index=target, doc_type=dtype, id=url_key):
                doc = {
                    "_id": url_key,
                    "_index": target,
                    "_type": dtype,
                    "_source": article['_source']
                }
                process.append(doc)
                # existing.add(key)
            remove.append({
                '_op_type': 'delete',
                '_index': source,
                '_type': dtype,
                '_id': article["_id"]})
        if len(process) > 0:
            com_ind = helpers.bulk(es, process, chunk_size=1000, request_timeout=200)
        else:
            com_ind = 0
        if len(remove) > 0:
            com_rem = helpers.bulk(es, remove, chunk_size=1000, request_timeout=200)
        else:
            com_rem = 0
        print("indexed", com_ind, "and removed", com_rem, "in batch", counter)
        # else:
        #     print("no valid documents in batch", counter)

        res = es.scroll(scroll_id=scroll, scroll='10m')


"""
            # article["_source"]["date_created"] = (datetime.strptime(article["_source"]["date_created"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            # article["_source"]["date_modified"] = (datetime.strptime(article["_source"]["date_modified"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            # article["_source"]["date_published"] = (datetime.strptime(article["_source"]["date_published"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
"""
