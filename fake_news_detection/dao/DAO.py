'''
Created on Jan 8, 2019

@author: daniele
'''
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article
from fake_news_detection.model.InterfacceComunicazioni import News
import itertools
import random
from elasticsearch import helpers
log = getLogger(__name__)

class DAONews:
    '''
    Rappresentazione della classe dao per l'interazione con le news
    '''

    def next(self,filter=None,languages=None):
        raise NotImplementedError()
    
    def all(self,filter=None,languages=None):
        raise NotImplementedError()
        
        
    def set_label(self,id,label):
        raise NotImplementedError()
    
    def create_doc_news(self,news):
        raise NotImplementedError()
    
    
    
class DAONewsElastic(DAONews):
    
    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_news #news_article_current
        self.docType = docType_article
        #self.bookmark=None
        
    def set_label(self,id,label):
        doc_up=  {
           '_op_type': 'update',
           '_index': self.index_name,
           '_type': self.docType,
           '_id': id,
           'doc': {'label':label}
        }
        helpers.bulk(self.es_client, [doc_up])

    def create_doc_news(self, news):
        doc_up=  {
           '_op_type': 'index',
           '_index': self.index_name,
           '_type': self.docType,
           '_source' : news
        }
        helpers.bulk(self.es_client, [doc_up])

        
    def next(self,filter=None,languages=None):
        body={
              'size': 1,
              'query': {
                'function_score':{
                "query":{
                'bool': {
                  'must': [
                    {
                      'bool': {
                        'should': [
                          {
                            'match': {
                              'label': ''
                            }
                          },
                          {
                            'bool': {
                              'must_not': {
                                'exists': {
                                  'field': 'label'
                                }
                              }
                            }
                          }
                        ]
                      }
                    }
                  ]
                },
              },
              'functions':[ 
                {
                  'random_score': 
                    {
                        "seed":random.randint(0,100000),
                        "field":"_seq_no"
                      }
                }
                ] 
              }
             }
            }
        if languages:
            if type(languages)==str:
                languages=[languages]
            elif type(languages)!=list:
                raise Exception
            d=dict()
            d["terms"]={"language":languages}
            body["query"]["function_score"]["query"]["bool"]["must"].append(d)
            
        if filter:
            body["query"]["function_score"]["query"]["bool"]["must"][0]["bool"]["should"][0]["match"]["label"]=filter
            
        print(body)
        res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
        if len(res['hits']['hits'])==0:
            #TODO:
            #GESTIRE NEL BACKEND PER PISU
            raise StopIteration()
        for el in res['hits']['hits']:
            id_doc=el['_id']
            publish=el["_source"].get("source_domain")
            url=el["_source"].get("url")
            #print(el["_source"])
            title=el["_source"].get("title")
            text=el["_source"].get("text")
            language=el["_source"].get("language")
            author=el["_source"].get("authors")
            return News(id_doc,url,title,text,author,publish,language)

    def all(self,filter=None,languages=None):
        body={
              'size': 3,
              'query': {
                'bool': {
                  'must': [
                    {
                      'bool': {
                        'should': [
                          {
                            'match': {
                              'label': ''
                            }
                          },
                          {
                            'bool': {
                              'must_not': {
                                'exists': {
                                  'field': 'label'
                                }
                              }
                            }
                          }
                        ]
                      }
                    }
                  ]
                },
              },
              'sort': [
                {
                  'date_created': 'desc'
                },
                {
                  '_uid': 'desc'
                }
              ]
            }
        if languages:
            if type(languages)==str:
                languages=[languages]
            elif type(languages)!=list:
                raise Exception
            d=dict()
            d["terms"]={"language":languages}
            body["query"]["bool"]["must"].append(d)
            
        if filter:
            body["query"]["bool"]["must"][0]["bool"]["should"][0]["match"]["label"]=filter
        while 1:
            if 'search_after' in body:
                del body['search_after']
                
            res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
            if len(res['hits']['hits'])==0:
                break
            while res['hits']['hits']:
            
                for el in res['hits']['hits']:
                    id_doc=el['_id']
                    source_domain=el["_source"].get("source_domain")
                    url=el["_source"].get("url")
                    #print(el["_source"])
                    title=el["_source"].get("title")
                    text=el["_source"].get("text")
                    language=el["_source"].get("language")
                    authors=el["_source"].get("authors")
                    yield News(id_doc,url,title,text,authors,source_domain,language)
                bookmark = [res['hits']['hits'][-1]['sort'][0], str(res['hits']['hits'][-1]['sort'][1])]
                body['search_after']=bookmark
                res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
        
if __name__ == '__main__':
    dao=DAONewsElastic()
    while 1: 
        k = dao.next(languages="pt")
        print(k.text,k.id)
        dao.set_label(k.id, "PISUBELLO")
    print(dao.next(languages="pt"))
    print(dao.next(languages="pt"))
    #===========================================================================
    # g=dao.all(languages="pt")
    #===========================================================================
    #print(d)
    #===========================================================================
    # while 1:
    #     print(next(g))    
    #===========================================================================
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        