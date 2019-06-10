'''
Created on Oct 24, 2018

@author: daniele
'''

from fake_news_detection.config.AppConfig import get_elastic_connector,\
    index_name_news, docType_article, dataset_beta, domains_index
import pandas as pd
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.utils.Exception import FandangoException
import os
from pip._vendor.html5lib.treebuilders import dom
from elasticsearch_dsl.search import Search, TransportError
import itertools
from fake_news_detection.dao.DAO import DAONewsElastic
from _collections import defaultdict
from pygments.unistring import Pe
#from fake_news_detection.services.Services import dao_news
from xml.etree import cElementTree as ET

log = getLogger(__name__)


class DAOTraining:
    def get_train_dataset(self):
        return NotImplementedError



class DAOTrainingPD:
    #dataset_beta togliere commento e metterlo nel path 
    def __init__(self, path = dataset_beta, delimiter='|'):
        self.path = path
        print(self.path)
        self.delimiter = delimiter
        
    def get_train_dataset(self, sample_size:float=1.0):
        print("\n\n > start of 'get_train_dataset()'")
        print('Read Train Guardian.csv')
        training_set= pd.read_csv(self.path +"/"+"guardian.csv",sep='\t') # dataset
        training_set['label']=1
        df=training_set
        print("shape after 'guardian.csv' -->", df.shape)
        
        training_set= pd.read_csv(self.path +"/fake_or_real_news.csv") # dataset
        df_app=training_set[['title','text','label']]
        df_app['label'] = df_app['label'].map({'FAKE': 0, 'REAL':1})
        df=df.append(df_app)
        print("shape after 'fake_or_real_news.csv' -->", df.shape)

        X=pd.read_csv(self.path+"/data.csv")
        X=X.rename(index=str, columns={"Label": "label", "Body": "text","Headline":"title"})
        X = X.drop(['URLs'], axis=1)
        df=df.append(X)
        print("shape after 'data.csv' -->", df.shape)
        with open(self.path+"/dataset_kafka.csv","r") as file:
            for r in file.readlines():
                items=r.strip().split("\t")
                if items[2]=='REAL': 
                    label=1 
                else: 
                    label=0
                title=items[3]
                text=items[4]
                df = df.append({'title': title,'text':text,'label':label}, ignore_index=True)

        print("shape after 'dataset_kafka.csv' -->", df.shape)

        ###################
        files=os.listdir(dataset_beta+"/articles")
        print(files)
        v=set()
        for f in files:
            e = ET.XML(open(dataset_beta+"/articles/"+f,"r").read())
            title=""
            text =""
            value =""
            for k in e:
                if k.tag=="mainText":
                    text=k.text
                
                if k.tag=="title":
                    title=k.text
    
                if k.tag=="veracity":
                    value=k.text
                    
            if value=='mostly false' or value=='mostly true':
                if value=='mostly false':
                    value="0"
                else:
                    value='1'
                df = df.append({'title': title,'text':text,'label':value}, ignore_index=True)

        print("shape after 'articles' -->", df.shape)
                
        #df=df_app
        df=df.dropna(subset = ['title','text','label'])
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
    
      
    def __init__(self,list_domains=None):
        self.es_client = get_elastic_connector()
        self.index_name = index_name_news 
        self.docType = docType_article
        self.list_domains=list_domains
        self.domains_index = domains_index
        
    
    
    def get_train_dataset(self,limit=1000):
        '''
        from a given file, it converts articles labeled into rows of a dataframe
        @param path_domain: str
        @return: dataf : dataframe pandas 
        '''
        list_df = []
        for domain in self.list_domains:
            label = domain[1]
            print(domain[0])
            list_documents = self.__get_news_from_domain(domain[0],limit)
            if len(list_documents)==0:
                continue
            print(domain[0],len(list_documents))
            
            df1 = pd.DataFrame.from_dict(list_documents)
            df1['label'] = label
            df1.dropna(inplace=True)
            # print(df1.shape)
            list_df.append(df1)
        
        dataf = pd.concat(list_df, axis= 0)
        #print(dataf.shape)
        #print( df1.head(5))
        print(dataf.groupby(['label']).agg(['count']))
        print("> end of 'get_train_dataset()'\n", dataf.columns)
        return dataf
 
    def __get_news_from_domain(self,domain,limit=100000):
        
        try:
            search = Search(using=self.es_client,index=self.index_name,doc_type=self.docType).query("term", source_domain=domain)
            response = search.execute()
            result_list=[]
            print("RESPONSE TOTAL:", response.hits.total)
            for c,hit in enumerate(itertools.islice(search.scan(),limit)):
                if len(hit.title.strip())>10 and len(hit.text.strip())>20:
                    result_list.append({"title":hit.title.strip(),  "text" : hit.text.strip()})
                    print(hit.title, hit.text)
                else:
                    print("scarto")
            return result_list
        except TransportError as e:
            print(e.info)
            
        
    def get_domains_from_elastic(self):
        
        domain_list = []
        body = {"query": {"match_all": {}}}
        dic_domain = defaultdict(list)       
        res = self.es_client.search(index= self.domains_index, body= body)
        for i in res['hits']['hits']:
            domain_list.append( (i['_source']['webdomain'], i['_source']['label']))
            if i['_source']['label'] =='FAKE':
                dic_domain['FAKE'].append(i['_source']['webdomain'])
            else:
                dic_domain['REAL'].append(i['_source']['webdomain'])
        print(dic_domain)
        return dic_domain
        
                 
        
    def __get_news_from_domainOLD(self,domain,limit = 2000):
        
        '''
        Given a certain domain, it searches for all the documents of that domain
        @param domain: str 
        @return: result_list : list of dicts
        '''
        
        result_list =[]
        #in case you want to take all the documents without a limit
        
        body2 = {
            "query": {
            "term" : { "source_domain" : domain } 
                }
            }
 
        res = self.es_client.count(index= self.index_name, doc_type=self.docType, body= body2)
        #size = res['count']
        size = limit
         
        if size == 0 :
            log.debug("no records for selected domain: {dmn}, it can't continue".format(dmn=domain))
            raise FandangoException("no records for selected domain: {dmn}, it can't continue".format(dmn=domain))
            
                    
        body = { "size": 20,
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
         
        body1 = {"size": 20,#1000
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
            if len(res['hits']['hits']) == 0:
                return [[res['_source']['title'], res['_source']['text']] for res in result['hits']['hits']]
            
            for el in res['hits']['hits']:
                result['hits']['hits'].append( el )
            bookmark = [res['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1]) ]
            print(bookmark)
            body1 = {"size": 20,#1000
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
            if len(res['_source']['title'])>0 and len(res['_source']['text'])>0 :  
                result_list.append({"title":res['_source']['title'],  "text" : res['_source']['text'] , "label" : "" })
         
        #print(result_list[0:2])
        log.debug("All articles from domain request are taken for training set building ")
        return result_list
        #return  [[res['_source']['title'], res['_source']['text']] for res in result['hits']['hits']]

                


if __name__ == '__main__':
    files=os.listdir(dataset_beta+"/articles")
    print(files)
    v=set()
    for f in files:
        e = ET.XML(open(dataset_beta+"/articles/"+f,"r").read())
        title=""
        text =""
        value =""
        for k in e:
            if k.tag=="mainText":
                text=k.text
            
            if k.tag=="title":
                title=k.text

            if k.tag=="veracity":
                value=k.text
                
        if value=='mostly false' or value=='mostly true':
            if value=='mostly false':
                value="0"
            else:
                value='1'
            v.add(text)
              
    print(len(v))
      
    #===========================================================================
    # dao_news=DAONewsElastic()
    # #list_domains = dao_news.get_domain()
    # #print( list_domains)
    # list_domains = [('www.thesun.co.uk','FAKE'),('sputniknews.com', 'FAKE')]
    # 
    # print(list_domains)
    # ii = DAOTrainingElasticByDomains(list_domains)
    # l= ii.get_train_dataset(limit = 10000)
    # print(l.shape)
    # print( l['title'].iloc[100])
    # print( l['text'].iloc[100])
    #===========================================================================
    #l.to_csv('/home/camila/Scrivania/fakedata1.csv', sep = '\t', index = False)
    
    #===========================================================================
    # 
    # oo = DAOTrainingElasticByDomains()
    # oo.get_domains_from_elastic()
    #===========================================================================
    #print(oo.get_domains_from_elastic())
    
    
    #ii = DAOTrainingElasticByDomains()
    #p.to_csv("/home/camila/Scrivania/Fandango_data.tsv",index = False, sep= "\t"

