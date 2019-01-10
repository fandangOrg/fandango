'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import index_name_claims, train_claims
from fake_news_detection.dao.ClaimsDAO import DAOClaimsElasticIngestion


log = getLogger(__name__)

class UploadClaims():

    def __init__(self):
        '''
        Constructor
        '''
        self.claims_getter = DAOClaimsElasticIngestion()
        self.log = getLogger(__name__)
        self.index_name_claims = index_name_claims
    
    def delete(self):
        """
        Delete an old index of claims before rebuild it
        """
        self.claims_getter.delete()
        
    def run_index_creation(self,name_file):
        """
        pipeline of operations to store claim
        @param name_file: str
        """ 
        self.claims_getter.create_new_index()
        lista_azioni = []
        lista_azioni = self.claims_getter.add_new_fields_and_index(train_claims+"/"+name_file, lista_azioni)
        self.claims_getter.bulk_new_index(lista_azioni)


    def similar_claims(self,text):
        """
        From a claim in input, get the most similar claims recorded
        @param text: str
        @return: lista_claim: list
        """
        return self.claims_getter.similarity_query(text)

        
        
def popolate():
    """
    pipeline to build an index claim  on elastic
    """
    I = UploadClaims()
    I.delete()
    I.run_index_creation('train.tsv')
    I.run_index_creation('test.tsv')
    I.run_index_creation('valid.tsv')
    
if __name__  == "__main__":
    
    
    I = UploadClaims()
    I.runIndexCreation('train.tsv')
    I.runIndexCreation('test.tsv')
    I.runIndexCreation('valid.tsv')
    I.similarClaims("dance")
    