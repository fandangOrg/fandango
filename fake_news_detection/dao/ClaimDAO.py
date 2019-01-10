'''
Created on 27 set 2018

@author: camila
'''

from fake_news_detection.config.AppConfig import  get_elastic_connector,\
    docType, mapping, index_name_claims, train_claims, dataset_beta
from fake_news_detection.utils.logger import getLogger
from elasticsearch import helpers
import csv
from fake_news_detection.utils.Exception import FandangoException
from nltk.data import path
import itertools

log = getLogger(__name__)


class DAOClaimInput:
    def all(self):
        raise NotImplementedError()
    
    
class DAOClaimInputDummy:
    
    def all(self):
        claims="ciao questo é il claim numero "
        for k in range(100):
            claim = {}
            claim["id_json"] = str(k)
            claim["label"] =  "label"+str(k)
            claim["claim"] =  claims+str(k)
            claim["topic"] = "topic"+str(k)
            claim["author"] = "author"+str(k)
            claim["role_of_the_authors"] = "role_of_the_authors"+str(k)
            yield claim
            
class DAOClaimInputCSV:
    def __init__(self,path,delimiter='\t'):
        self.path=path
        self.delimeter=delimiter
        
    def all(self):
        with open( self.path) as f:
            reader = csv.reader(f, delimiter='\t')
            for r in reader:
                claim = {}
                claim["id_json"] = r[0]
                claim["label"] =  r[1]
                claim["claim"] =  r[2]
                claim["topic"] = r[3]
                claim["author"] = r[4]
                claim["role_of_the_authors"] = r[5]
                yield claim
        
 

class DAOClaimsOutput:
    
    def restart_source(self):
        raise NotImplementedError()
        
    def add_claim(self, claim):
        raise NotImplementedError()
    
    def add_claims(self, dao:DAOClaimInput):
        raise NotImplementedError()
    
    def get_similarity_claims_from_text(self,text):
        raise NotImplementedError()


class DAOClaimsOutputElastic:
    
    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_claims 
        self.docType = docType   
        
    def get_similarity_claims_from_text(self,text):
        """
        retrieve a similar claim, querying against elastic
        @param text: str
        @return lista_claim: list
        """
        body1 = {
                  "query": {
                    "bool": {
                      "should": [
                        {
                          "match_phrase": {
                            "claim": text
                            
                          }
                        }
                      ],
                      "minimum_should_match": "60%",
                      "must": [
                        {
                          "match": {
                            "claim": text
                          }
                        }
                      ]
                    }
                  }
                    ,
                    "highlight" : {
                        "pre_tags" : ["<b>"],
                        "post_tags" : ["</b>"],
                        "fields" : {
                            "claim" : 
                                {
                                 "number_of_fragments":0
                                }
                        }
                    }
                }
        try:
            res = self.es_client.search(index= self.index_name, body= body1)
        except Exception as e:
            log.error("Could not perform similarity claim query: {err}".format(err=e))
            raise FandangoException("Could not perform similarity claim query: {err}".format(err=e))
        lista_claim =[]
        for r in res['hits']['hits']:
            if r["_score"]>5:
                lista_claim.append( {"score": r['_score'], "claim": r["highlight"]["claim"][0]} )               
                log.debug("New similar claim founded, original claim: {ori}, found: {cl}".format(ori=text, cl=r['_source']['claim'])) 
            
        return lista_claim
       
    def __delete_index(self):
        #TODO:RIMETTERE IL DELETE DEL TEMPLATE
        """
        remove index from ES
        """
        try:
            self.es_client.indices.delete(self.index_name, ignore=[400,404])
        except:
            log.info("Could not delete index: {ind}".format(ind=self.index_name))
            raise FandangoException("Could not delete index: {ind}".format(ind=self.index_name))
            
            
    def restart_source(self):
        """
        Check if the claim index exists in elasticsearch. If don't, it creates a new index
        """
        try:
            for templ in self.es_client.cat.templates(format="json"):
                if templ["index_patterns"]== "[*]":
                    self.es_client.indices.delete_template(templ["name"])
        except:
            pass
        
        if self.es_client.indices.exists(index=self.index_name):
            self.__delete_index()
            
        with open(mapping , "r") as f:
            body = f.read()
            try:
                self.es_client.indices.create(index = self.index_name, body = body)
                log.info("Mapping successfully loaded for index: {ind}".format(ind =self.index_name))
            except:
                log.info("Could not create new index: {ind}".format(ind =self.index_name))
                raise FandangoException("Could not create new index: {ind}".format(ind = self.index_name))


    def add_claim(self, claim):
        raise NotImplementedError()
    
    def add_claims(self, dao:DAOClaimInput):
        lista_claims = []
        for c,claim in enumerate(dao.all()):
            if c%1000==0:
                print("number claims",c)
            lista_claims.append( {
                    '_op_type': 'index',
                    '_index': self.index_name,
                    '_type': self.docType,
                    '_source': claim
        
                })
        print("start insert in elastic")
        self.__bulk_new_index(lista_claims)
        
    def __bulk_new_index(self, lista_azioni):
        """
        bulk a list of operations in elastic 
        @param lista_azioni: list 
        """
        for success, info in helpers.parallel_bulk(self.es_client, lista_azioni):
            if not success:
                self.log.info("Can't index documents, an error has occurred: {err}".format(err=info))
                raise FandangoException("Can't index documents, an error has occurred: {err}".format(err=info))
                
        log.info("New index successfully indexed")

    
    
       
if __name__ == '__main__':
    name=train_claims+"/train.tsv"
   # dao_input= DAOClaimInputCSV(name)
    #for claim in dao_input.all():
    #    print(claim)
        
    dao_input= DAOClaimInputDummy()
    dao_output = DAOClaimsOutputElastic()
    #dao_output.restart_source()
    #dao_output.add_claims(dao_input)
    a=dao_output.get_similarity_claims_from_text("ciao questo é il claim numero 4")
    print(a)
    #popola_all()
    
    
    
                    
        