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
dataset_beta = pkg_resources.resource_filename("fake_news_detection.resources", "")  # @UndefinedVariable
static_folder = pkg_resources.resource_filename("static", "")  # @UndefinedVariable
##################################################################################################################à
#dataset_beta = pkg_resources.resource_filename("fake_news_detection.resources", "")  # @UndefinedVariable
 
#---------------------------->ELASTIC VARIABLES<----------------------------------------------------------------------------
index_name = config.get("elasticsearch", "index_name")
index_name_news = os.environ.get("INDEX_ELASTIC_NEWS") or config.get("elasticsearch", "index_news") or "news_article_current"
index_name_output= os.environ.get("INDEX_ELASTIC_NEWS_ANNOTATION") or config.get("elasticsearch", "index_news_annotation") or "news_annotation_lvt"
docType_article = os.environ.get("DOCTYPE_NEWS") or config.get("elasticsearch", "doctype_news") or "article"
train_claims = pkg_resources.resource_filename("fake_news_detection.resources.claims", "")  # @UndefinedVariable
mapping = pkg_resources.resource_filename("fake_news_detection.config", "new_mapping.json")  # @UndefinedVariable
mapping_claim= pkg_resources.resource_filename("fake_news_detection.config", "new_mapping.json")  # @UndefinedVariable
domains_train= pkg_resources.resource_filename("fake_news_detection.resources", "url_list_labeled.txt")  # @UndefinedVariable
docType = os.environ.get("INDEX_ELASTIC") or config.get("elasticsearch", "doctype")
index_name_claims = os.environ.get("NEW_MAPPED_INDEX") or config.get("elasticsearch", "claim_index")
domain_index= os.environ.get("DOMAIN_INDEX") or config.get("elasticsearch", "domain_index")
domain_docType= os.environ.get("DOMAIN_DOCTYPE") or config.get("elasticsearch", "domain_docType")
domain_file=pkg_resources.resource_filename("fake_news_detection.resources", "new_mapping.json") 
number_item_to_train= os.environ.get("SIZE_DOMAIN") or 1000000
index_author_org = os.environ.get("INDEX_ELASTIC_AUTHORS") or config.get("elasticsearch", "index_author_org") or "index_author"
#mapping_domain_index = pkg_resources.resource_filename("fake_news_detection.config", "mapping_domain.json") # @UndefinedVariable
#mapping_claim = os.environ.get("MAPPING_CLAIM") or config.get("elasticsearch", "mapping_claim")
#dataset_beta = os.environ.get("DATASET_BETA") or config.get("dataprova", "dataset_beta")
index_name_article = os.environ.get("INDEX_NAME_ARTICLE") or config.get("elasticsearch", "article_index") 



#--------------------------->EXTERNAL SERVICES VARIABLES<-------------------------------------------------------------------------
url_service_upm = os.environ.get("URL_SERVICE_UPM") or config.get("configurationservice", "upm_service_url") 
url_service_certh = os.environ.get("URL_SERVICE_CERTH") or config.get("configurationservice", "certh_service_url") 

######################################################################################
#############KAFKA CONFIG #############À
url_kafka = os.environ.get("KAFKA_URL") or config.get("kafka", "url")  
port_kafka = os.environ.get("KAFKA_PORT") or config.get("kafka", "port")  
topic_input_kafka  = os.environ.get("TOPIC_INPUT") or config.get("kafka", "topic_input") 
topic_output_kafka = os.environ.get("TOPIC_OUTPUT") or config.get("kafka", "topic_output")
group_id="lvt_group2"
n_consumer = os.environ.get("N_CONSUMER") or config.get("kafka", "consumer")

if __name__ == '__main__':
    print(static_folder)

# dataset_beta = os.environ.get("DATASET_BETA") or config.get("dataprova", "dataset_beta")
    
