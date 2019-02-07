'''
Created on Oct 24, 2018

@author: daniele
'''

from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article, dataset_beta, domains_train
import pandas as pd
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.utils.Exception import FandangoException
import os
from fake_news_detection.utils.file_reader import read_domain


log = getLogger(__name__)


class DAOTraining:
    def get_train_dataset(self):
        return NotImplementedError



class DAOTrainingPD:

    def __init__(self, path=dataset_beta, delimiter='\t'):
        self.path = path
        self.delimiter = delimiter
        
    def get_train_dataset(self, sample_size:float=1.0):
        print("\n\n > start of 'get_train_dataset()'")
        training_set= pd.read_csv(self.path +"/"+"fake.csv") # dataset
        #print(training_set.dropna(subset = ['title'])['title'])
        df=training_set.dropna(subset = ['title','text'])
        df=df[['title','text']]
        df['label']='FAKE'
        print("shape after 'fake.csv' -->", df.shape)

        training_set= pd.read_csv(self.path +"/"+"guardian.csv",sep='\t') # dataset
        training_set['label']='REAL'
        df=df.append(training_set)
        print("shape after 'guardian.csv' -->", df.shape)

        training_set= pd.read_csv(self.path +"/fake_or_real_news.csv") # dataset
        df_app=training_set[['title','text','label']]
        df=df.append(df_app)
        print("shape after 'fake_or_real_news.csv' -->", df.shape)

        #df=df_app
        df=df.dropna(subset = ['title','text','label'])
        #df['text']=df['text'].swifter.apply(clean_text)
        #df['title'].swifter.apply(clean_text)
        #df1= pd.DataFrame(columns=['title','text','label'])
        for dir in os.listdir(self.path ):
            if dir == "fake":
                for file in os.listdir(self.path  +"/"+ dir):
                    with open(self.path +"/"+  dir + "/" +file) as f:
                        dizio = dict()
                        dizio['title'] = " ".join(f.readlines()[:1])
                        dizio['text'] = " ".join(f.readlines()[2:])
                        dizio['label'] = 'FAKE'
                        df1  = pd.DataFrame([dizio], columns=dizio.keys())
                        df = pd.concat([df, df1], axis =0)
                        
            elif dir == "legit":
                for file in os.listdir(self.path+ "/"  + dir):
                    with open(self.path +"/" + dir + "/"+ file) as f:
                        dizio = dict()
                        dizio['title'] = " ".join(f.readlines()[:1])
                        dizio['text'] = " ".join(f.readlines()[1:])
                        dizio['label'] = 'REAL'
                        df1  = pd.DataFrame([dizio], columns=dizio.keys())
                        df = pd.concat([df, df1], axis =0)

        if sample_size < 1.0:
            df = df.sample(frac=sample_size)

        print("final shape -->", df.shape)
        print(df.groupby(['label']).agg(['count']))
        print("> end of 'get_train_dataset()'\n")
        return df



class DAOTrainingElastic:

    def __init__(self):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_news 
        self.docType = docType_article
        
    def get_train_dataset(self, filter=None,languages=None):
        responseL = []
        body = {
                    "query":{
                    'bool': {
                      'must': [
                        {
                          'bool': {
                            'must': [
                              {
                                'match': {
                                  'label': ''
                                }
                              },
                              {
                                'bool': {
                                  'must': {
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
                    }
                    }
                    }

        if languages:
            if type(languages)==str:
                languages=[languages]
            elif type(languages)!=list:
                raise FandangoException("Languages should be a string or a list not {cl}".format(cl=type(languages)))
            d=dict()
            d["terms"]={"language":languages}
            body["query"]["bool"]["must"].append(d)
                             
        if filter:
            log.debug("Searching for news with label: {lbl}".format(lbl= filter))
            body['query']['bool']['must'][0]["bool"]["must"][0]["match"]["label"]=filter
            
        try:
            res = self.es_client.search(index=self.index_name, body= body,doc_type=self.docType)
        except Exception as e:
            log.error("Could not query against elasticsearch: {err}".format(err=e))
            raise FandangoException("Could not query against elasticsearch: {err}".format(err=e))
        
        if len(res['hits']['hits'])==0:
            log.debug("There are no hits for your research: {q}".format(q=body))
            raise FandangoException("There are no hits for your research")
        
        for el in res['hits']['hits']:
            responseL.append( {"title": el['_source']['title'],"text":el['_source']['text'],"label":el['_source']['label'] } )
        
        return pd.DataFrame(responseL)



class DAOTrainingElasticByDomains():
    
      
    def __init__(self,list_domains=read_domain(domains_train)):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_news 
        self.docType = docType_article
        self.list_domains=list_domains
    
    def get_train_dataset(self):
        '''
        from a given file, it converts articles labeled into rows of a dataframe
        @param path_domain: str
        @return: dataf : dataframe pandas 
        '''
        list_df = []
        for domain in self.list_domains:
            label = domain[1]
            list_documents = self.__get_news_from_domain(domain[0])
            print(domain[0])
            df1 = pd.DataFrame.from_dict(list_documents)
            df1['label'] = label
            
            print(df1.shape)
            list_df.append(df1)
        
        dataf = pd.concat(list_df, axis= 0)
        print(dataf.shape)
        print( df1.head(5))
        return dataf

    def __get_news_from_domain(self,domain):
        '''
        Given a certain domain, it searches for all the documents of that domain
        @param domain: str 
        @return: result_list : list of dicts
        '''
        result_list =[]
        body2 = {
            "query": {
            "term" : { "source_domain" : domain } 
                }
            }

        res = self.es_client.count(index= self.index_name, doc_type=self.docType, body= body2)
        size = res['count']
        
        if size == 0 :
            log.debug("no records for selected domain: {dmn}, it can't continue".format(dmn=domain))
            raise FandangoException("no records for selected domain: {dmn}, it can't continue".format(dmn=domain))
        
        body = { "size": 10,
                    "query": {
                        "term" : {
                            "source_domain" : domain
                        }
                    },
                    "sort": [
                        {"date_published": "asc"},
                        {"_uid": "desc"}
                    ]
                }
        
        result = self.es_client.search(index= self.index_name, doc_type=self.docType, body = body)
        bookmark = [result['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1]) ]
        
        body1 = {"size": 10,
                    "query": {
                        "term" : {
                            "source_domain" : domain
                        }
                    },
                    "search_after": bookmark,
                    "sort": [
                        {"date_published": "asc"},
                        {"_uid": "desc"}
                    ]
                }

        while len(result['hits']['hits']) < size:
            res = self.es_client.search(index= self.index_name, doc_type=self.docType, body= body1)
            for el in res['hits']['hits']:
                result['hits']['hits'].append( el )
            bookmark = [res['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1]) ]
            body1 = {"size": 10,
                    "query": {
                        "term" : {
                            "source_domain" : domain
                        }
                    },
                    "search_after": bookmark,
                    "sort": [
                        {"date_published": "asc"},
                        {"_uid": "desc"}
                    ]
                }
        
        for res in result['hits']['hits']:
            result_list.append({"title":res['_source']['title'],  "text" : res['_source']['text'] , "label" : "" })
        
        #print(result_list[0:2])
        log.debug("All articles from domain request are taken for training set building ")
        return result_list
    
        #return  [res['_source']['title'], res['_source']['text']] for res in result['hits']['hits']

                

if __name__ == '__main__':
    #oo = DAOTrainingPD(dataset_beta)
    #print(oo.get_train_dataset())
    ii = DAOTrainingElasticByDomains()
    p = ii.get_train_dataset_from_domains("/home/camila/Scrivania/url_list_labeled.txt")
    p.to_csv("/home/camila/Scrivania/Fandango_data.tsv",index = False, sep= "\t")
    
    
    
    