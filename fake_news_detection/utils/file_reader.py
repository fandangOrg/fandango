'''
Created on 7 feb 2019

@author: daniele
'''
import os
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.utils.Exception import FandangoException

log = getLogger(__name__)

def read_domain(path_domain):
    '''
    given a file, return a list of domain with label
    @param path_domain: str
def __init__(self):
    self.es_client = get_elastic_connector()
    self.index_name = index_name_news 
    self.docType = docType_article
    

def get_train_dataset_from_domains(self,path_domain):
    
    list_domains = self.read_domain(path_domain)
    list_df = []
    
    for domain in list_domains:
    @return: domain_list_labeled: list
    '''
    domain_list_labeled = []
    if os.path.getsize(path_domain) < 1:
        #check if file is empty
        log.debug("empty file {pth}".format(pth = path_domain))
        raise FandangoException("empty file {pth}".format(pth = path_domain))
            
    with open(path_domain, "rb") as f:
        for line in f: 
            line = line.decode('utf-8-sig')
            line = line.split(',')      
            domain_list_labeled.append((line[0].strip(), line[1].strip()))
            log.debug('domain with annotation is {tup}'.format(tup = domain_list_labeled)  )                        
    
    return domain_list_labeled
