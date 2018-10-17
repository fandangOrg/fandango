'''
Created on 2 ott 2018
@author: camila
'''
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import numpy as np 
import re
from fake_news_detection.utils.logger import getLogger



class MyClass(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.pathcsv = r"/home/camila/Downloads/fake_or_real_news.csv"
        self.esclient = Elasticsearch("localhost:9200")
        self.index_name = "indexfakenews"
        self.docType = "_doc"
        self.log = getLogger(__name__)
    
    def clean_text(self, text):
    
        text = text.lower()
        text = re.sub(r"what's", "what is ", text)
        text = re.sub(r"\'s", " ", text)
        text = re.sub(r"\'ve", " have ", text)
        text = re.sub(r"can't", "can not ", text)
        text = re.sub(r"n't", " not ", text)
        text = re.sub(r"i'm", "i am ", text)
        text = re.sub(r"\'re", " are ", text)
        text = re.sub(r"\'d", " would ", text)
        text = re.sub(r"\'ll", " will ", text)
        text = re.sub(r"\'scuse", " excuse ", text)
        text = re.sub('\W', ' ', text)
        text = re.sub('\s+', ' ', text)
        text = text.strip(' ')
        return text      
    
    def run(self):
        
        operationL = []
        df = pd.read_csv(self.pathcsv, encoding = 'utf-8')
        df[df.columns[2]] = df[df.columns[2]].map(lambda com : self.clean_text(com))
        df[df.columns[1]] = df[df.columns[1]].map(lambda com : self.clean_text(com))
        #df['text'].iloc[0]

        
        for i in range(1,df.shape[0]):
                documento = {
                    "id" : str(df['Unnamed: 0'].iloc[i]),
                    "text" : str(df['text'].iloc[i]), 
                    "title": str(df['title'].iloc[i]),
                    "label": str(df['label'].iloc[i])}
                
                operationL.append( {
                            '_op_type': 'index',
                            '_index': self.index_name,
                            '_type': self.docType,
                            '_source': documento,
                        })
        
        #print(operationList[1])
        try:
            helpers.bulk(self.esclient, operationL)
        except Exception as e:
            self.log.debug("error:  {err}".format(err= e))
            raise Exception
            
        
    '''
    def indicizeOnElastic(self ):    
        for success,info in helpers.parallel_bulk(self.esclient, self.run()):
            if not success:
                print(info)
    '''
         
if __name__ ==  '__main__':
    oo = MyClass()
    oo.run()
    del oo