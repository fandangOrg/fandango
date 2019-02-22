'''
Created on 19 feb 2019

@author: camila
'''
from fake_news_detection.config.AppConfig import get_elastic_connector, index_author_org, docType

class DAOAuthorOutputElastic:
    '''
    classdocs
    '''


    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_author_org
        self.docType = docType
        
    def outout_author_organization(self,author_or_org):
        
        
        try :
            return self._get_author(author_or_org)
        except:
            return self._get_organization(author_or_org)
    
    
    def _get_author(self, author):
        
        body = {"query": {"term":{"author_name.keyword": {"value": author}}}}
        
        res = self.es_client.search(index=self.index_name, body= body)
        if len(res['hits']['hits']) > 0 :
            r = res['hits']['hits'][0]['_source']
            s = (r['author_name'], r['author_score'])
            print(s)
            return int(float(r['author_score'])*100)
        else: 
            return -1
       
        
    def _get_organization(self, org):
        
        body = {"query": {"term":{"org_name.keyword": {"value": org}}}}
        
        res = self.es_client.search(index=self.index_name, body= body)
        print(res['hits']['hits'])
        if len(res['hits']['hits']) > 0: 
            r = res['hits']['hits'][0]['_source']
            s = (r['org_name'], r['org_score'])
            print(s)
            return int(float(r['org_score'])*100)
        else: 
            return -1

       
        
        
        

if __name__ == '__main__':
    d = DAOAuthorOutputElastic()
    #d._get_author("Rohantha De Silva")
    #d._get_organization("dgdgfdgd")
    #d.outout_author_organization("Rohantha De Silva")
        
        

        
      
        
        
        