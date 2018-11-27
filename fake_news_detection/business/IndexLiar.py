'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.dao.ElasticDao import Search
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import new_mapped_index, train_claims
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
    
    def delete(self):
        S = Search()
        S.delete()
        
    def runIndexCreation(self,name_file):
        
        S = Search()
        S.CreateNewIndex()
        lista_azioni = []
        lista_azioni = S.AddNewFieldsandINDEX(train_claims+"/"+name_file, new_mapped_index, lista_azioni)
        S.BulkNewIndex(lista_azioni)

    def similarClaims(self,text, max_claims = 3):
        
        S= Search()
        r = S.similarity_query(text)
        #jsonclaims = json.dumps(r)
        
        print(r)
        return r

        
        
def popolate():
    I = IndexLiar()
    I.delete()
    I.runIndexCreation('train.tsv')
    I.runIndexCreation('test.tsv')
    I.runIndexCreation('valid.tsv')
    
if __name__  == "__main__":
    
    
    I = IndexLiar()
    I.runIndexCreation('train.tsv')
    I.runIndexCreation('test.tsv')
    I.runIndexCreation('valid.tsv')
    I.similarClaims("dance")
    