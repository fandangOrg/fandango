'''
Created on Jan 8, 2019

@author: daniele
'''
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article
from fake_news_detection.model.InterfacceComunicazioni import News
import random
from elasticsearch import helpers
from fake_news_detection.utils.Exception import FandangoException
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
        self.index_name = index_name_news 
        self.docType = docType_article

        
    def set_label(self,id,label):
        """
        add a new field label in a doc with that id
        @param id: str
        @param label: str
        """
        self.log.info("new annotation submitted: id:" ,id,'label:', label)
        doc_up=  {
           '_op_type': 'update',
           '_index': self.index_name,
           '_type': self.docType,
           '_id': id,
           'doc': {'label':label}
        }
        self.bulk_on_elastic(doc_up)

    def create_doc_news(self, news):
        """
        prepare a bulk query to index a new document
        @param news: str
        """
        doc_up=  {
           '_op_type': 'index',
           '_index': self.index_name,
           '_type': self.docType,
           '_source' : news.__dict__
        }
        self.bulk_on_elastic(doc_up)
        
        
    def bulk_on_elastic(self, doc_up):
        """
        perform a bulk query in elastic
        @param doc_up: dict
        """
        try:
            helpers.bulk(self.es_client, [doc_up])
        except Exception as e:
            self.log.error("Could not perform bulk query: {err}".format(err=e))
            raise FandangoException("Could not perform bulk query: {err}".format(err=e))
        self.log.info("Bulk query successfully submitted to elastic: {doc_up}".format(doc_up=doc_up))

        
    def next(self,filter=None,languages=None):
        """
        generate new doc to annotate, filtered by label and language
        @param filter: str
        @param languages: str
        @return: response_news: News
        """
        self.log.info("New doc to annotate in {lang}".format(lang=languages))
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
            self.log.debug("Searching for claim with label: {lbl}".format(lbl= filter))
            body["query"]["function_score"]["query"]["bool"]["must"][0]["bool"]["should"][0]["match"]["label"]=filter
            
        try:
            res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
        except Exception as e:
            self.log.error("Could not query against elasticsearch: {err}".format(err=e))
            raise FandangoException("Could not query against elasticsearch: {err}".format(err=e))
        if len(res['hits']['hits'])==0:
            raise StopIteration()
        for el in res['hits']['hits']:
            id_doc=el['_id']
            publish=el["_source"].get("source_domain")
            url=el["_source"].get("url")
            title=el["_source"].get("title")
            text=el["_source"].get("text")
            language=el["_source"].get("language")
            author=el["_source"].get("authors")
            response_news = News(id_doc,url,title,text,author,publish,language)
            self.log.debug("New doc to annotate generated: {doc}".format(doc=response_news))
            return response_news

 
if __name__ == '__main__':
    dao=DAONewsElastic()
    while 1: 
        k = dao.next(languages="ptiii")
        print(k.text,k.id)
        dao.set_label(k.id, "FAKE")
    print(dao.next(languages="pt"))
    print(dao.next(languages="pt"))
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        