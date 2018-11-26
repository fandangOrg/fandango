'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.dao.ElasticDao import Search
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import new_mapped_index
#import json

class IndexLiar():
    '''
    run if you want to create a index on elastic search
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
        lista_azioni = S.AddNewFieldsandINDEX("/home/camila/eclipse-workspace/fandango-fake-news/fake_news_detection/resources/LIARDATASET/train.tsv", new_mapped_index, lista_azioni)
        S.BulkNewIndex(lista_azioni)

    def similarClaims(self,text, max_claims = 3):
        
        S= Search()
        r = S.similarity_query(text)
        #jsonclaims = json.dumps(r)
        
        print(r)
        return r

        
        
            
if __name__  == "__main__":
    
    
    I = IndexLiar()
    #I.runIndexCreation()
    I.similarClaims("dance")
    