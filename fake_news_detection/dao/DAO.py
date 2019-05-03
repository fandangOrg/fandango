'''
Created on Jan 8, 2019

@author: daniele
'''


from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article, domain_index, domain_docType,\
    index_name_output, index_name_article
from fake_news_detection.model.InterfacceComunicazioni import News,\
    News_DataModel
import random
from elasticsearch import helpers
from fake_news_detection.utils.Exception import FandangoException
from ds4biz_predictor_core.dao.predictor_dao import FSPredictorDAO
from elasticsearch_dsl.search import Search
import random 
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
        self.index_name_output = index_name_output
        self.docType = docType_article
        self.domain_name_index = domain_index
        self.docType_domain = domain_docType
        self.index_name_article = index_name_article
        self.mapping_path = None
        self.check_index_exists()
        
    def GetCounterDef(self):
        body = {"query": {"exists" : { "VALUE" : "label" }}}
        try:
            print(body)
            res = self.es_client.search(index=self.index_name_output, body= body,doc_type=self.docType)
        except Exception as e:
            log.error("Could not query against elasticsearch: {err}".format(err=e))
            raise FandangoException("Could not query against elasticsearch: {err}".format(err=e))
        
        return res['hits']['total']
    
    def GetCounterTemp(self, language):
        
        
        body = {
                "query": {
                    "bool": {
                        "must": [
                          {
                            "exists": {
                                "field": "label"
                                      }
                                },
                          {
                            "match_phrase": {
                              "language": language
                            }
                          }
                              ]
                            }
                          }
            }

        
        try:
            #print(body)
            res = self.es_client.count(index=self.index_name_output, body= body,doc_type=self.docType)
            print(self.docType,self.index_name_output)
        except Exception as e:
            log.error("Could not query against elasticsearch: {err}".format(err=e))
            raise FandangoException("Could not query against elasticsearch: {err}".format(err=e))
        return(int(res['count']))
    
    def create_source(self,news):
        """
        create doc for annotated domain
        @param news: obj
        """
        lista_operazioni = []
        for notizia in news.list_url.split("\n"):
            source = {
                "label": news.label,
                "domain" : notizia,
                "lang" : news.lang
                }
            lista_operazioni.append( {
           '_op_type': 'index',
           '_index': self.domain_name_index,
           '_type': self.docType_domain,
           '_source': source
           })
        self.bulk_on_elastic(lista_operazioni)
        
        
    

    def get_domain(self):
        """
        create doc for annotated domain
        @param news: obj
        """
        body={
              "query": {
                "match_all": {}
              }
             }
        
        search = Search(using=self.es_client,index=self.domain_name_index,doc_type=self.docType_domain)
        search.from_dict(body)
        response = search.execute()
        print("RESPONSE TOTAL:", response.hits.total)
        l = [] 
        for r in response['hits']['hits']:
            l.append((r["_source"]["domain"],r["_source"]["label"]))
        return l
            
    def _get_article_By_id(self,id):
        search = Search(using=self.es_client,index=self.index_name,doc_type=self.docType)\
                .query("term", _id=id)
        response = search.execute()
        print("RESPONSE TOTAL:", response.hits.total)
        for r in response['hits']['hits']:
                print(r["_source"])
                return r["_source"]

    def set_label(self,id,label,type_annotation):
        """
        add a new field label in a doc with that id
        @param id: str
        @param label: str
        """
        news=self._get_article_By_id(id).__dict__
        news["label"] = label
        news["type_annotation"] =type_annotation
        log.info("new annotation submitted: id: {id},label: {lbl}".format(id=id,lbl= label))
        doc_up=  {
           #'_op_type': 'update',
           '_op_type': 'index',
           '_index': self.index_name_output,
           '_type': self.docType,
           #'_id': id,
           #'doc': {'label':label,'type_annotation':type_annotation}
            '_source' : news
        }
        self.bulk_on_elastic(doc_up)
    '''
    def create_doc_news(self, news):
        """
        prepare a bulk query to index a new document
        @param news: str
        """
        news["authors"]=[d["author"] for d in news["authors"]]
        doc_up=  {
           '_op_type': 'index',
           '_index': self.index_name_output,
           '_type': self.docType,
           '_source' : news
        }
        print(doc_up)
        self.bulk_on_elastic(doc_up)
    '''
        
    def create_doc_news(self,dic_final):
        """
        prepare a bulk query to index a new document
        @param news: str
        """
        
        doc_up =  {
           '_op_type': 'index',
           '_index': self.index_name_article,

           '_type': 'doc',
           '_source' : dic_final
        }
        print(doc_up)
        self.bulk_on_elastic(doc_up)   
    
    def check_index_exists(self):

        if not self.es_client.indices.exists(index=self.index_name, ignore=404):
            if self.mapping_path is not None:
                with open(self.mapping_path, "r") as g:
                    index_def = g.read()
                    self.es_client.indices.create(index=self.index_name, body=index_def)
                    log.info("{ind} Index settings and mapping process completed".format(ind=self.index_name))
            else:
                self.es_client.indices.create(index=self.index_name)
                log.info("{ind} Index settings and mapping process completed".format(ind=self.index_name))
    
        return self.es_client.indices.exists(index=self.index_name, ignore=404)
    
    def bulk_on_elastic(self, doc_up):
        """
        perform a bulk query in elastic
        @param doc_up: dict
        """
        if not isinstance(doc_up, list):
            doc_up = [doc_up]
        try:
            helpers.bulk(self.es_client, doc_up)
        except Exception as e:
            log.error("Could not perform bulk query: {err}".format(err=e))
            raise FandangoException("Could not perform bulk query: {err}".format(err=e))
        log.info("Bulk query successfully submitted to elastic: {doc_up}".format(doc_up=doc_up))

        
    def next(self,filter=None,languages=None):
        """
        generate new doc to annotate, filtered by label and language
        @param filter: str
        @param languages: str
        @return: response_news: News
        """
        log.info("New doc to annotate in {lang}".format(lang=languages))
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
                        #"field":"_seq_no"
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
            log.debug("Searching for claim with label: {lbl}".format(lbl= filter))
            body["query"]["function_score"]["query"]["bool"]["must"][0]["bool"]["should"][0]["match"]["label"]=filter
            
        try:
            print(body)
            res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
        except Exception as e:
            log.error("Could not query against elasticsearch: {err}".format(err=e))
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
            response_news = News(url,title,text,author,publish,language,id_doc)
            log.debug("New doc to annotate generated: {doc}".format(doc=response_news))
            return response_news

 
########MODELLI#############
class FSMemoryPredictorDAO(FSPredictorDAO):

    def __init__(self, path):
        FSPredictorDAO.__init__(self, path)

    def delete_from_memory(self, nome_modello):
        if nome_modello in self.predictors:
            del self.predictors[nome_modello]
            
if __name__ == '__main__':
    pass
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        