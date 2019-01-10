'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import index_name_claims, train_claims
from fake_news_detection.dao.ClaimsDAO import DAOClaimsElasticIngestion
from fake_news_detection.dao.ClaimDAO import DAOClaimsOutputElastic,\
    DAOClaimInputCSV


log = getLogger(__name__)

 
def similar_claims(self,dao_output,text):
    """
    From a claim in input, get the most similar claims recorded
    @param text: str
    @return: lista_claim: list
    """
    return dao_output.get_similarity_claims_from_text(text)

        

    
        
def popola(nomefile,dao_output):
    dao_input= DAOClaimInputCSV(nomefile)
    dao_output.add_claims(dao_input)
    
def popola_all(dao_output):
    dao_output.restart_source()
    nomefile=train_claims+"/train.tsv"
    popola(nomefile,dao_output)
    nomefile=train_claims+"/test.tsv"
    popola(nomefile,dao_output)
    nomefile=train_claims+"/validate.tsv"
    popola(nomefile,dao_output)
    
if __name__  == "__main__":
    
    
    I = UploadClaims()
    I.runIndexCreation('train.tsv')
    I.runIndexCreation('test.tsv')
    I.runIndexCreation('valid.tsv')
    I.similarClaims("dance")
    