'''
Created on 13 lug 2018

@author: michele
'''
import configparser
import os
import pkg_resources 
from configparser import ConfigParser, RawConfigParser
from elasticsearch import Elasticsearch
  
def getConfig(fname=None):     
    if fname == None:  # cambiare tmp
        fname = pkg_resources.resource_filename("fake_news_detection.config", 'properties.ini')  # @UndefinedVariable     
        
             
    config = ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()  
    config = RawConfigParser()  
    config.read(fname)     
    return config 

config = getConfig() 
 

def get_elastic_connector():
    # username = os.environ.get("USERNAME_ELASTIC") or config["elasticsearch"][ "username"]
    # password = os.environ.get("PWD_ELASTIC") or config['elasticsearch']['password'] 
    # esConnector = Elasticsearch(url, http_auth = (username, pwd))
    # esConnector = Elasticsearch(url, http_auth=(username,password))
    url = os.environ.get("URL_ELASTIC") or config["elasticsearch"][ "url"]
    print(url)
    esConnector = Elasticsearch(url, max_size=25)
    print(esConnector.ping())
    return esConnector

# FORMAT = "%(asctime)s %(levelname)s %(name)s.%(funcName)s() - %(message)s"
# logging.basicConfig(format=FORMAT, filename=self.config.get("default", "log_file"), level=logging.DEBUG)
        
#----------------------------->DEFAULT VARIABLES<--------------------------------------------------------
log_folder = os.environ.get("LOG_FOLDER") or config.get("default", "log_folder")  or  pkg_resources.resource_filename("fake_news_detection.resources.log", "")  # @UndefinedVariable
BASEURL = os.environ.get("BASEURL_SERVICE") or config["service"]["url"]
BASEPORT = os.environ.get("BASEPORT_SERVICE") or config["service"]["port"]

picklepath = os.environ.get("MODEL_PATH") or  pkg_resources.resource_filename("fake_news_detection.resources.model", "")  # @UndefinedVariable
dataset_beta =  config.get("train", "path")  or pkg_resources.resource_filename("fake_news_detection.resources", "")   # @UndefinedVariable 
static_folder = pkg_resources.resource_filename("new_static", "")  # @UndefinedVariable
path_training = os.environ.get("PATH_FOR_TRAININGFILE") or config.get("default", "path_training")
resources_path = pkg_resources.resource_filename("fake_news_detection.resources", "")
template_path = pkg_resources.resource_filename("fake_news_detection.templates", "")

##################################################################################################################à
#dataset_beta = pkg_resources.resource_filename("fake_news_detection.resources", "")  # @UndefinedVariable
 
#---------------------------->ELASTIC VARIABLES<----------------------------------------------------------------------------
index_name_news = os.environ.get("INDEX_ELASTIC_NEWS") or config.get("elasticsearch", "index_news") or "news_article_current"
docType_article = os.environ.get("DOCTYPE_NEWS") or config.get("elasticsearch", "doctype_news") or "article"
mapping = pkg_resources.resource_filename("fake_news_detection.config", "new_mapping.json")  # @UndefinedVariable
docType = os.environ.get("INDEX_ELASTIC") or config.get("elasticsearch", "doctype")
domain_file=pkg_resources.resource_filename("fake_news_detection.resources", "new_mapping.json") 
number_item_to_train= os.environ.get("SIZE_DOMAIN") or 1000000
#mapping_domain_index = pkg_resources.resource_filename("fake_news_detection.config", "mapping_domain.json") # @UndefinedVariable
#mapping_claim = os.environ.get("MAPPING_CLAIM") or config.get("elasticsearch", "mapping_claim")
#dataset_beta = os.environ.get("DATASET_BETA") or config.get("dataprova", "dataset_beta")
index_name_article = os.environ.get("INDEX_NAME_ARTICLE") or config.get("elasticsearch", "article_index") 
domains_index = os.environ.get("INDEX_NAME_DOMAIN") or config.get("elasticsearch", "domain_index") 


#--------------------------->EXTERNAL SERVICES VARIABLES<-------------------------------------------------------------------------
url_service_preprocessing = os.environ.get("URL_SERVICE_UPM") or config.get("configurationservice", "preprocessing_service_url") 
url_service_media = os.environ.get("URL_SERVICE_CERTH") or config.get("configurationservice", "media_service_url") 
url_service_authors = os.environ.get("URL_SERVICE_UPM") or config.get("configurationservice", "authors_service_url")
url_similar_claims = os.environ.get("URL_SERVICE_UPM") or config.get("configurationservice", "url_similar_claims")
######################################################################################
#############KAFKA CONFIG #############À


url_kafka = os.environ.get("KAFKA_URL") or config.get("kafka", "url")  
port_kafka = os.environ.get("KAFKA_PORT") or config.get("kafka", "port")  
topic_input_kafka  = os.environ.get("TOPIC_INPUT") or config.get("kafka", "topic_input") 
topic_output_kafka = os.environ.get("TOPIC_OUTPUT") or config.get("kafka", "topic_output")
group_id="lvt_group22"
n_consumer = os.environ.get("N_CONSUMER") or config.get("kafka", "consumer")

if __name__ == '__main__':
    print(static_folder)

# dataset_beta = os.environ.get("DATASET_BETA") or config.get("dataprova", "dataset_beta")
    
