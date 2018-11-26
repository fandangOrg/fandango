'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.dao.ElasticDao import Search
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import new_mapped_index
import pandas as pd

class IndexLiar():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Search = Search()
        self.log = getLogger(__name__)
        self.new_mapped_index = new_mapped_index

    def runIndexCreation(self):
        
        S = Search()
        S.CreateNewIndex()
        lista_azioni = []
        lista_azioni = S.AddNewFieldsandINDEX("/home/camila/workspace/fandango-fake-news/fake_news_detection/LIARDATASET/train.tsv", new_mapped_index, lista_azioni)
        S.BulkNewIndex(lista_azioni)

    def similarClaims(self,text, max_claims = 3):
        
        S= Search()
        r = S.similarity_query(text)
        #print(r[0:max_claims])
        
        p = pd.DataFrame(r[0:max_claims])
        print(p[['label','claim']])
        return p[['label','claim']]
            
        #return r[0:max_claims]
        
        
            
if __name__  == "__main__":
    
    
    I = IndexLiar()
    #I.runIndexCreation()
    I.similarClaims("dance")
    