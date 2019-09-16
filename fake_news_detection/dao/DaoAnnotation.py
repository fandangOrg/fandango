'''
Created on 13 set 2019

@author: daniele
'''
from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_annotation, index_name_news, docType_article, mapping_annotation
from fake_news_detection.utils.logger import getLogger
from elasticsearch_dsl.search import Search
from fake_news_detection.utils.Exception import FandangoException
from elasticsearch import helpers
import random
from fake_news_detection.model.InterfacceComunicazioni import News
    
log = getLogger(__name__)

class DAOElasticAnnotation():
    
    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_news
        self.docType = docType_article
        self.index_annotation = index_annotation
        self.check_index_exists()
        
    def check_index_exists(self):
        if not self.es_client.indices.exists(index=self.index_annotation, ignore=404):
                with open( mapping_annotation, "r") as g:
                    index_def = g.read()
                    self.es_client.indices.create(index=self.index_annotation, body=index_def)
                log.info("{ind} Index settings and mapping process completed".format(ind=self.index_annotation))
        
        
    def bulk_on_elastic(self, doc_up):
        """
        perform a bulk query in elastic
        @param doc_up: dict
        """
        if not isinstance(doc_up, list):
            doc_up = [doc_up]
        try:
            helpers.bulk(self.es_client, doc_up,refresh='wait_for')
        except Exception as e:
            log.error("Could not perform bulk query: {err}".format(err=e))
            raise FandangoException("Could not perform bulk query: {err}".format(err=e))
        log.info("Bulk query successfully submitted to elastic: {doc_up}".format(doc_up=doc_up))

    
    def insert_new_annotation(self,id,author,language,annotation):
        d={'identifier':id,
           "author":author,
           "inLanguage":language,
           'annotation':annotation
        }
        """
        prepare a bulk query to index a new document
        @param news: str
        """
        
        doc_up =  {
           '_op_type': 'index',
           '_index': self.index_annotation,
           '_type': 'doc',
           '_source' : d
        }
        self.bulk_on_elastic(doc_up)  
        
    def _get_missed_annoation(self,author,language="en"):
        print("LANGUAGE",language)
        body={
              "size": 0,
              "query": { "match": {"inLanguage":language} },
              "aggs": {
                "group_by_id": {
                  "terms": {
                    "field": "identifier",
                    "size": 2000,
                    "order": {
                        "_count" : "asc" 
                    }
                  } 
                }
              }
            }
        response = self.es_client.search(index=self.index_annotation, body= body )
        ids= response['aggregations']['group_by_id']['buckets']
        for r in ids:
            count= r["doc_count"]
            if count < 3:
                #Ha fatto l'annotazione già
                print("check autore per la news",r["key"])
                if self._check_author_done(r["key"],author):
                    continue
                else:
                    return r["key"]
        return None
    
    def _get_counter_annoation(self,author,language="en"):
        print("LANGUAGE",language)
        body={
              "size": 0,
              "query": { "match": {"inLanguage":language} },
              "aggs": {
                "group_by_id": {
                  "terms": {
                    "field": "identifier",
                    "size": 2000,
                    "order": {
                        "_count" : "asc" 
                    }
                  } 
                }
              }
            }
        response = self.es_client.search(index=self.index_annotation, body= body )
        ids= response['aggregations']['group_by_id']['buckets']
        return len(ids)                
        
    def _check_author_done(self,id,author):
        """
        """
        body={ "size": 10,
                "query": {
                  "match_phrase": {
                    "identifier": id
                  }
                }
              }
        response = self.es_client.search(index=self.index_annotation, body= body )
        #print("RESPONSE TOTAL:", response['hits']['hits'])
        for r in response['hits']['hits']:
            news= r["_source"]
            print(news['author'],author)
            if author.lower()==news['author'].lower():
                return True
        return False
    
    def _check_news_done(self,id):
        """
        """
        body={ "size": 10,
                "query": {
                  "match_phrase": {
                    "identifier": id
                  }
                }
              }
        response = self.es_client.search(index=self.index_annotation, body= body )
        #print("RESPONSE TOTAL:", response['hits']['hits'])
        for r in response['hits']['hits']:
            news= r["_source"]
            return True
        return False
    
    def _get_news(self, id):
            
        body = {
                "query": {
                  "match_phrase": {
                    "identifier": id
                  }
                }
              }
        
        res = self.es_client.search(index=self.index_name, body= body)
        if len(res['hits']['hits']) >0:
            news = res['hits']['hits'][0]["_source"]
            return news
        else:
            log.debug('news you want to add already exists')
            return None
        
    def _parser_news(self,news):
        id_doc=news['identifier']
        publish=news.get("sourceDomain")
        url=news.get("url")
        title=news.get("headline")
        text=news.get("articleBody")
        language=news.get("inLanguage")
        author=news.get("authors")
        response_news = News(url,title,text,author,publish,language,id_doc)
        log.debug("New doc to annotate generated: {doc}".format(doc=response_news))
        return response_news
        
    def next_news(self,author,language="en"):
        """
        """
        log.info("...........SEARCH MISSED ANNOTATION MIN 3 AUTHORS, LANG  "+language+" AUTHOR "+author)
        #PRIMO STEP VERIFICO SE C'È QUALE ANNOTAZIONE PENDENTE, ALTRIMENTI PRENDE NEWS A CASO
        id=self._get_missed_annoation(author,language )
        if id is not None:
            news=self._get_news(id)
            return self._parser_news(news)
        #['identifier'],news['headline'],news.get('topic',"?"),news['inLanguage']
        k=1300
        while True:
            k-=1
            if k<0: raise StopIteration
            log.info("    NUOVA NEWS DAL DATALAKE AUTHORS, LANG  "+language+" AUTHOR "+author+" --> "+str(k))
    
            body={
               "size": 1,
               "query": {
                  "function_score": {
                        "query": { "match": {"inLanguage":language} 
                                  },
                        "boost": "5",
                        "random_score": {}, 
                        "boost_mode":"multiply"
                  }
               }
            }
            response = self.es_client.search(index=self.index_name, body= body )
            #print("RESPONSE TOTAL:", response['hits']['hits'])
            for r in response['hits']['hits']:
                news= r["_source"]
                print('ID NEWS RANDO',r["_source"]['identifier'])
                if not self._check_news_done(r["_source"]['identifier']):
                    return self._parser_news(news)
            #return news['identifier'],news['headline'],news.get('topic',"?"),news['inLanguage']
    
    
    
    
    
    
if __name__ == '__main__':
    dao=DAOElasticAnnotation()
    print(dao.next_news("author", "en"))
    for k in range(1,20):
        news=dao.next_news("author2")
        print(news)
        dao.insert_new_annotation(news.id, "author2", news.language, random.choice(["FAKE","REAL"]))
 
     
    
    
    
    
    
    
    