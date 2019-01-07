'''
Created on 13 lug 2018

@author: michele
'''
import codecs
import logging
import configparser
import os
import pkg_resources 
from configparser import ConfigParser, RawConfigParser
from elasticsearch import Elasticsearch
  
def getConfig(fname=None):     
    if fname == None:                                                           #cambiare tmp
        fname = pkg_resources.resource_filename("fake_news_detection.config", 'properties.ini')  # @UndefinedVariable     
        
             
    config = ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()  
    config = RawConfigParser()  
    config.read(fname)     
    return config 

config = getConfig() 

# FORMAT = "%(asctime)s %(levelname)s %(name)s.%(funcName)s() - %(message)s"
# logging.basicConfig(format=FORMAT, filename=self.config.get("default", "log_file"), level=logging.DEBUG)
        

log_folder = os.environ.get("LOG_FOLDER") or config.get("default", "log_folder")  or  pkg_resources.resource_filename("fake_news_detection.resources.log", "")# @UndefinedVariable
BASEURL = os.environ.get("BASEURL_SERVICE") or config["service"]["url"]
BASEPORT= os.environ.get("BASEPORT_SERVICE") or config["service"]["port"]

picklepath = pkg_resources.resource_filename("fake_news_detection.resources.model", "")  # @UndefinedVariable
dataset_beta = pkg_resources.resource_filename("fake_news_detection.resources", "")  # @UndefinedVariable
static_folder = pkg_resources.resource_filename("static", "")  # @UndefinedVariable
train_claims = pkg_resources.resource_filename("fake_news_detection.resources.claims", "")# @UndefinedVariable

mapping = pkg_resources.resource_filename("fake_news_detection.resources.claims", "liarmapping.json")# @UndefinedVariable

def getEsConnector():
    url= os.environ.get("URL_ELASTIC") or config["elasticsearch"][ "url"]
        #username = os.environ.get("USERNAME_ELASTIC") or config["elasticsearch"][ "username"]
        #password = os.environ.get("PWD_ELASTIC") or config['elasticsearch']['password'] 
        #esConnector = Elasticsearch(url, http_auth = (username, pwd))
     #esConnector = Elasticsearch(url, http_auth=(username,password))
    esConnector = Elasticsearch(url, max_size=25)
    return esConnector

index_name= os.environ.get("INDEX_ELASTIC") or config.get("elasticsearch", "indexfakenews")
docType = os.environ.get("INDEX_ELASTIC") or config.get("elasticsearch", "doctype")
pathFileLastDate = os.environ.get("pathFileLastDate") or config.get("default", "fileLastDate")
#mapping = os.environ.get("MAPPING_ELASTIC") or config.get("elasticsearch", "mapping")
new_mapped_index = os.environ.get("NEW_MAPPED_INDEX") or config.get("elasticsearch", "new_mapped_index")

if __name__ == '__main__':
    print(static_folder)

# dataset_beta = os.environ.get("DATASET_BETA") or config.get("dataprova", "dataset_beta")
    
