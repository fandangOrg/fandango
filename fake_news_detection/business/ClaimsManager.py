'''
Created on 6 nov 2018

@author: camila
'''
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.config.AppConfig import train_claims
from fake_news_detection.dao.ClaimDAO import DAOClaimInputCSV,\
    DAOClaimsOutputElastic


log = getLogger(__name__)

 
def similar_claims(dao_output, text):
    """
    From a claim in input, get the most similar claims recorded
    @param dao_output: str
    @param text: str
    @return: lista_claim: list
    """
    return dao_output.get_similarity_claims_from_text(text)

    
        
def popola(nomefile,dao_output):
    """
    populate storage system with claims
    @param nomefile: str
    @param dao_output: str
    """
    dao_input= DAOClaimInputCSV(nomefile)
    dao_output.add_claims(dao_input)
    
def popola_all(dao_output):
    """
    Inizialize storage system 
    @param dao_output: str
    """
    dao_output.restart_source()
    nomefile=train_claims+"/train.tsv"
    popola(nomefile,dao_output)
    nomefile=train_claims+"/test.tsv"
    popola(nomefile,dao_output)
    nomefile=train_claims+"/valid.tsv"
    popola(nomefile,dao_output)
    
if __name__  == "__main__":
    out = DAOClaimsOutputElastic()
    #similar_claims(dao_output=out,text="trump gay")
    popola_all(DAOClaimsOutputElastic())