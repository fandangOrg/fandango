'''
Created on 27 set 2018

@author: camila
'''

from fake_news_detection.config.AppConfig import  get_elastic_connector,\
    docType, mapping, index_name_claims
from fake_news_detection.utils.logger import getLogger
from elasticsearch import helpers
import csv
from fake_news_detection.utils.Exception import FandangoException
from nltk.data import path

class DAOClaimInput:
    def all(self):
        raise NotImplementedError()
    
    
class DAOClaimInputCSV:
    def __init__(self,path,delimiter='\t'):
        self.path=path
        self.delimeter=delimiter
        
    def all(self):
        r=search_all_clam():
        for r[]hit
            claim = {}
            claim["id_json"] = r[0]
            claim["label"] =  r[1]
            claim["claim"] =  r[2]
            claim["topic"] = r[3]
            claim["author"] = r[4]
            claim["role_of_the_authors"] = r[5]
            yield claim
class DAOClaimInputES:
    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_claims 
        self.docType = docType   
        
    def all(self):
        with open(self.path) as f:
            reader = csv.reader(f, self.delimiter)
            for r in reader:
                claim = {}
                claim["id_json"] = r[0]
                claim["label"] =  r[1]
                claim["claim"] =  r[2]
                claim["topic"] = r[3]
                claim["author"] = r[4]
                claim["role_of_the_authors"] = r[5]
                yield claim

        
class DAOClaimsIngestion:
    '''
    Rappresentazione della classe dao per l'interazione con le claims
    '''

    def delete(self):
        raise NotImplementedError()
    
    def similarity_query(self,text):
        raise NotImplementedError()
                
    def create_new_index(self):
        raise NotImplementedError()
    
    def add_clams_from_csv(self, csv_file, crea_indice, lista_azioni):
        raise NotImplementedError()
    def add_clams_from_ex(self, csv_file, crea_indice, lista_azioni):
        raise NotImplementedError()
    def add_clams_from_db(self, csv_file, crea_indice, lista_azioni):
        raise NotImplementedError()
    def add_claim(self, claim):
        raise NotImplementedError()
    def add_claims(self, daoInput):
        raise NotImplementedError()
            
    def create_doc_news(self,news):
        raise NotImplementedError()
    
    def bulk_new_index(self, lista_azioni):
        raise NotImplementedError()


class DAOClaimsElasticIngestion(DAOClaimsIngestion):
    def __init__(self): 
        self.es_client = get_elastic_connector()
        self.index_name = index_name_claims 
        self.docType = docType   
        self.log = getLogger(__name__)
        
    def __delete(self):
        """
        remove index from ES
        """
        try:
            self.ESclient.indices.delete(self.index_name, ignore=[400,404])
        except:
            self.log.info("Could not delete index: {ind}".format(ind=self.index_name))
            raise FandangoException("Could not delete index: {ind}".format(ind=self.index_name))
            
                
    def similarity_query(self,text):
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
            res = self.ESclient.search(index= self.index_name, body= body1)
        except Exception as e:
            self.log.error("Could not perform similarity claim query: {err}".format(err=e))
            raise FandangoException("Could not perform similarity claim query: {err}".format(err=e))
        lista_claim =[]
        for r in res['hits']['hits']:
            if r["_score"]>5:
                lista_claim.append( {"score": r['_score'], "claim": r["highlight"]["claim"][0]} )               
                self.log.debug("New similar claim founded, original claim: {ori}, found: {cl}".format(ori=text, cl=r['_source']['claim'])) 
            
        return lista_claim
    
    
    
    def create_new_index(self):
        """
        Check if the claim index exists in elasticsearch. If don't, it creates a new index
        """
        if not self.ESclient.indices.exists(index=self.index_name):
            with open(mapping , "r") as f:
                body = f.read()
                try:
                    self.ESclient.indices.create(index = self.index_name, body = body)
                    self.log.info("Mapping successfully loaded for index: {ind}".format(ind =self.index_name))
                except:
                    self.log.info("Could not create new index: {ind}".format(ind =self.index_name))
                    raise FandangoException("Could not create new index: {ind}".format(ind = self.index_name))

    def add_clams_from_csv(self, csv_file, crea_indice, lista_azioni):
        """
        Populate an index, retrieving the data from a csv file
        @param csv_file: str
        @param lista_azioni: list
        @return: lista_azioni:list 
        """ 
        with open(csv_file) as f:
            reader = csv.reader(f, delimiter='\t')
            for r in reader:
                fields ={}
                        claim
                fields["id_json"] = r[0]
                fields["label"] =  r[1]
                fields["claim"] =  r[2]
                fields["topic"] = r[3]
                fielddao_claim_outputs["author"] = r[4]
                fields["role_of_the_authors"] = r[5]
                
                lista_azioni.append( {
                    '_op_type': 'index',
                    '_index': self.index_name,
                    '_type': self.docType,
                    '_source': fields
        
                })
    
        return lista_azioni

    def append_claim_all(self, dao):
        for cl in dao.all():
            
            self.append_claim(cl)
    
    def add(self,claim):
        elstastich            
    def add_clams_from_db(self, csv_file, crea_indice, lista_azioni):
        raise NotImplementedError()
    def add_clams(self, input_obj, crea_indice, lista_azioni):
        raise NotImplementedError()
    
    def add_new_fields_and_index_from_ex(self,exle_file, lista_azioni):
        
    def add_new_fields_and_index_from_mysql(self,exle_file, lista_azioni):
    def add_new_fields_and_index_from_mongodb(self,exle_file, lista_azioni):
    def add_new_fields_and_index_from_solr(self,exle_file, lista_azioni):
        
    def add_new_fields_and_index_from_csv(self,csv_file, lista_azioni):
        """
        Populate an index, retrieving the data from a csv file
        @param csv_file: str
        @param lista_azioni: list
        @return: lista_azioni:list 
        """ 
        daooutputclaim = DAOClaimsElasticIngestion()
        with open(ex_file) as f:
            reader = exl.reader(f, delimiter='\t')
            for r in reader:
                daooutputclaim.add(r)
                fields ={}
                        
                fields["id_json"] = r[0]
                fields["label"] =  r[1]
                fields["claim"] =  r[2]
                fields["topic"] = r[3]
                fields["author"] = r[4]
                fields["role_of_the_authors"] = r[5]
                
                lista_azioni.append( {
                    '_op_type': 'index',
                    '_index': self.index_name,
                    '_type': self.docType,
                    '_source': fields
        
                })
    
        return lista_azioni
         
    def bulk_new_index(self, lista_azioni):
        """
        bulk a list of operations in elastic 
        @param lista_azioni: list 
        """
        for success, info in helpers.parallel_bulk(self.es_client, lista_azioni):
            if not success:
                self.log.info("Can't index documents, an error has occurred: {err}".format(err=info))
                raise FandangoException("Can't index documents, an error has occurred: {err}".format(err=info))
                
        self.log.info("New index successfully indexed")

    
        
        
        
                    
        