'''
Created on Oct 24, 2018

@author: daniele
'''

from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article, dataset_beta
import pandas as pd
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.utils.Exception import FandangoException



log = getLogger(__name__)

class DAOTraining:
    def get_train_dataset(self):
        return NotImplementedError
    
class DAOTrainingPD:
    def __init__(self, path, delimiter='\t'):
        self.path = path
        self.delimiter = delimiter
        
    def get_train_dataset(self):
        training_set= pd.read_csv(dataset_beta+"/"+"fake.csv") # dataset
        #print(training_set.dropna(subset = ['title'])['title'])
        df=training_set.dropna(subset = ['title','text'])
        
        df=df[['title','text']]
        df['label']='FAKE'
        training_set= pd.read_csv(dataset_beta+"/"+"guardian.csv",sep='\t') # dataset
        training_set['label']='REAL'
        df=df.append(training_set)
        training_set= pd.read_csv(dataset_beta+"/fake_or_real_news.csv") # dataset
        df_app=training_set[['title','text','label']]
        df=df.append(df_app)
        #df=df_app
        df=df.dropna(subset = ['title','text','label'])
        #df['text']=df['text'].swifter.apply(clean_text)
        #df['title'].swifter.apply(clean_text)
        print(df.groupby(['label']).agg(['count']))
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
                raise Exception
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

if __name__ == '__main__':
    oo = DAOTrainingElastic()
    print(oo.get_train_dataset(filter="FAKE"))