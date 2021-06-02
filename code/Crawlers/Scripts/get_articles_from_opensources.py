import newspaper
import datetime
from elasticsearch import Elasticsearch
import hashlib


# connect to elasticsearch
es = Elasticsearch(['127.0.0.1'], http_auth=('elastic', 'XEPfUca9VU'), port=9200)
# these are the indices that we will use
index_current = 'fake_opensources_com_current'
archive_index = 'fake_opensources_com_archive'
# this is the document fields mapping
mapping = {'properties': {
    'ancestor': {'type': 'text'},
    'descendant': {'type': 'boolean'},
    'version': {'type': 'long'},
    'title': {'type': 'text'},
    'description': {'type': 'text'},
    'summary': {'type': 'text'},
    'text': {'type': 'text'},
    'keywords': {'type': 'keyword'},
    'language': {'type': 'keyword'},
    'authors': {'type': 'text'},
    'date_download': {'type': 'date', "format":"yyyy-MM-dd HH:mm:ss"},
    'date_modify': {'type': 'date', "format":"yyyy-MM-dd HH:mm:ss"},
    'date_publish': {'type': 'date', "format":"yyyy-MM-dd HH:mm:ss"},
    'top_image': {'type': 'text'},
    'images': {'type': 'text'},
    'videos': {'type': 'text'},
    'url': {'type': 'keyword'},
    'source_domain': {'type': 'keyword'},
    'localpath': {'type': 'text', 'index' : False},
    'filename': {'type': 'text', 'index' : False},
    'texthash': {'type': 'keyword', 'index' : False},
    'fakeness': {'type': 'keyword'}
    }
}

# if elasticsearch indices do not exist, create them
if not es.indices.exists(index_current):
    es.indices.create(index=index_current, ignore=[400, 404])
    es.indices.put_mapping(index=index_current, doc_type='article', body=mapping)
if not es.indices.exists(archive_index):
    es.indices.create(index=archive_index, ignore=[400, 404])
    es.indices.put_mapping(index=archive_index, doc_type='article', body=mapping)

# open the csv file that contains the urls
with open("proper_urls_from_opensources.csv", 'r') as src:
    for line in src:
        # each line has a url and a type of fakeness
        url, tpe = line.split(",")
        print("building url", url)
        # newspaper3k has a function that builds an article tree from a base url
        paper = newspaper.build(url, memoize_articles=False)
        print("iterating articles")
        # for each article in the tree
        for article in paper.articles:
            try:
                # download the article, parse it and use nlp to extract info
                article.download()
                article.parse()
                article.nlp()
                # create a shell to put info in the correct fields
                store = dict()
                ancestor = None
                version = 1
                # check if article has been downloaded in the past (exists in index)
                request = es.search(index=index_current, body={'query': {'match': {'url': article.url}}})
                if request['hits']['total'] > 0:
                    old_version = request['hits']['hits'][0]
                    if old_version['_source']['url'] == article.url:
                        # if article exists and no changes are detected, goto next article
                        if hashlib.sha256(article.text.encode('utf-8')).hexdigest() == old_version['_source']['texthash']:
                            continue
                        # else move old version to archive index and store new version using the same doc id
                        old_version['_source']['descendant'] = True
                        downloaded = old_version['_source']['date_download']
                        es.index(index=archive_index, doc_type='article', body=old_version['_source'])
                        ancestor = old_version['_id']  # get the new id
                        version += 1
                # add links to old version of article if it exists
                store['ancestor'] = ancestor if ancestor else ""
                store['version'] = version
                store['descendant'] = False
                # get the relevant info to add to the document fields
                store['title'] = article.title
                store['description'] = article.meta_description
                store['summary'] = article.summary
                store['text'] = article.text
                store['keywords'] = list(article.keywords)
                store['language'] = article.meta_lang
                store['authors'] = article.authors
                # if we don't detect a date in the article, use the current date
                store['date_modify'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if store['version'] == 1:
                    store['date_download'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    store['date_download'] = downloaded
                if article.publish_date:
                    store['date_publish'] = article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    store['date_publish'] = store['date_download']
                store['top_image'] = article.top_image
                store['images'] = list(article.images)
                store['videos'] = list(article.movies)
                store['url'] = article.url
                store['source_domain'] = article.source_url
                # we don't actually keep a raw copy of the html so filename and localpath are irrelevant
                store['filename'] = ""
                store['localpath'] = ""
                store['texthash'] = hashlib.sha256(article.summary.encode('utf-8')).hexdigest()
                store['fakeness'] = tpe
                # add document to elasticsearch index
                es.index(index=index_current, doc_type='article', id=ancestor, body=store)
                print('.')
            except newspaper.article.ArticleException:
                print('*')
        print(" ")
        print("done with source", url)
