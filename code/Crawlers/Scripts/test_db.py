import sqlite3

all_ = []
act_ = []
name = 'generalstatic'

db = sqlite3.connect("website/db.sqlite3")
cursor = db.execute("SELECT id FROM sources_crawler WHERE name='%s';" % name)
crawler_id = cursor.fetchone()[0]
cursor = db.execute("UPDATE sources_newssite SET active=1 WHERE crawler_id=%s;" % crawler_id)
db.commit()
cursor.close()
db.close()


cursor = db.execute("SELECT id, base_url FROM sources_newssite WHERE crawler_id=%s;" % crawler_id)
cursor = db.execute("SELECT id, base_url FROM sources_newssite;")
for id, url in cursor:
    all_.append(url)

act_ = []
db = sqlite3.connect("website/db.sqlite3")
cursor = db.execute("SELECT id FROM sources_crawler WHERE name='%s';" % name)
crawler_id = cursor.fetchone()[0]
cursor = db.execute("SELECT id, base_url FROM sources_newssite WHERE active=1 AND crawler_id=%s;" % crawler_id)
for id, url in cursor:
    act_.append(url)

db.close()


working = set()

with open("website/working.csv", "r") as inp:
    for line in inp:
        a, b = line.split(",")
        working.add(".".join(a.strip().split(".")[-2:]))
        working.add(a.strip())


change = []
for url in all_:
    if url.lstrip("https://").split("/")[0] in working:
        change.append(url)
    elif ("www." + url.lstrip("https://").split("/")[0]) in working:
        change.append(url)
    elif ".".join(url.lstrip("https://").split("/")[0].split(".")[-2:]) in working:
        change.append(url)


db = sqlite3.connect("website/db.sqlite3")
cursor = db.execute("SELECT id FROM sources_crawler WHERE name='%s';" % name)
crawler_id = cursor.fetchone()[0]

for url in change:
    cursor = db.execute("UPDATE sources_newssite SET active=1 WHERE base_url='%s';" % url)
    # print(url)

db.commit()


from elasticsearch import Elasticsearch


mapping = {'properties': {
    'title': {'type': 'text'},
    # 'headline': {'type': 'text'},
    'text': {'type': 'text'},
    # 'article_body': {'type': 'text'},
    'images': {'type': 'text'},
    'videos': {'type': 'text'},
    'date_created': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss"},
    'date_modified': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss"},
    'date_published': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss"},
    'authors': {'type': 'text'},
    'source_domain': {'type': 'keyword'},
    # 'publisher': {'type': 'keyword'},
    'summary': {'type': 'text'},
    'description': {'type': 'text'},
    'keywords': {'type': 'keyword'},
    'language': {'type': 'keyword'},
    'top_image': {'type': 'text'},
    'url': {'type': 'keyword'},
    'texthash': {'type': 'keyword', 'index': False},
    # 'fakeness': {'type': 'keyword'},
    # 'briefclaim': {'type': 'text'},
    # 'about': {'type': 'text'},      # FK to Topic
    # 'mentions': {'type': 'text'}    # FK to Entity
    'ancestor': {'type': 'text'},
    'version': {'type': 'long'},
}}


es = Elasticsearch(['127.0.0.1'], port=9900)

index_current = 'news_article_current'
es.indices.create(index=index_current, ignore=[400, 404])

es.indices.put_mapping(index=index_current, doc_type='article', body=mapping)













