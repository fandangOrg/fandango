# -*- coding: utf-8 -*-

# ====================================================================================
# ------------------------- GLOBAL VARIABLES PREPROCESSING ---------------------------
# ====================================================================================
import coloredlogs, logging
import warnings, os
from helper.country_information import country_domains
from helper.helper import download_ner_models


warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

thread = None
service = None
offline_threads: list = []
country_domains: dict = country_domains

# Pre-processing Params
default_field = 'Anonymous'
org_default_field = 'N/A'
person_es_index = "fdg-ap-person"
org_es_index = "fdg-ap-organization"
idf_es_index = "crawled-articles"
ner_library = "spacy"

# Ports and Hosts
# Add environment variables
host = os.getenv("HOST_PORT") if "HOST_PORT" in os.environ else "0.0.0.0"
port = int(os.getenv("API_PORT")) if "API_PORT" in os.environ else 5001


""" Elasticsearch environment variables"""
if os.getenv('ELASTICSEARCH_SERVER') is not None:
    es_host = str(os.getenv('ELASTICSEARCH_SERVER'))
else:
    es_host = "localhost"

if os.getenv('ELASTICSEARCH_PORT') is not None:
    es_port = str(os.getenv('ELASTICSEARCH_PORT'))
else:
    es_port = "9200"

if os.getenv('ELASTICSEARCH_INDEX_ANNOT') is not None:
    temp_es_index = str(os.getenv('ELASTICSEARCH_INDEX_ANNOT'))
else:
    temp_es_index = "article_preprocessed_temp"

""" Kafka environment variables"""
if os.getenv('KAFKA_SERVER') is not None:
    kf_host = str(os.getenv('KAFKA_SERVER'))
else:
    kf_host = "localhost"

if os.getenv('KAFKA_PORT') is not None:
    kf_port = str(os.getenv('KAFKA_PORT'))
else:
    kf_port = "9092"

if os.getenv('KAFKA_TOPIC_CONSUMER') is not None:
    topic_consumer = str(os.getenv('KAFKA_TOPIC_CONSUMER'))
else:
    topic_consumer = 'input_raw'

if os.getenv('KAFKA_TOPIC_PRODUCER') is not None:
    topic_producer = str(os.getenv('KAFKA_TOPIC_PRODUCER'))
else:
    topic_producer = 'input_preprocessed'

kafka_server = kf_host + ":" + kf_port
group_id = 'upm_group'

# Process name
offline_service_name = "Offline service"
online_service_name = "Online service"
manual_annotation_service_name = "Manual Annotation service"
experimental_service_name = "Experimental Offline service"

service_name = "Pre-processing"
error_msg = "An error occurred when applying pre-processing"
running_msg = "Running"
aborted_msg = "Aborted"
stop_msg = "Stopped"
already_stop_msg = "The service is already stopped"
countries_websites = ["spain", "italy", "greece", "belgium", "uk", "usa"]
resources_dir = "resources"
csv_filepath = "domains.csv"

# HTTP RESPONSES
http_response_500: str = "Internal Server Error"
http_response_200: str = "Successful Operation"
http_response_422: str = "Invalid Input"
http_response_400: str = "Bad Request"
http_response_403: str = "HTTP Connection Error"


# Global params sourceRank
open_rank_api_key: str = os.getenv("OPEN_RANK_API_KEY") if \
    "OPEN_RANK_API_KEY" in os.environ else "4ss0ow0kw4ok8cssks8g0gc8gcscso0o8w48o0o0"

whois_api_key: str = os.getenv("WHOIS_API_KEY") if \
    "WHOIS_API_KEY" in os.environ else "at_yxzY2kbPMpkeZZzyYbbD0ZdNmFMNk"

news_api_key: str = os.getenv("NEWS_API_KEY") if \
    "NEWS_API_KEY" in os.environ else "424993da91574290853321e8413c8f8c"


consumer_key: str = os.getenv("TW_CONSUMER_KEY") if \
    "TW_CONSUMER_KEY" in os.environ else "WcIJMyBF3spFEtRGHwqDlAKDT"
consumer_secret: str = os.getenv("TW_CONSUMER_SECRET") if \
    "TW_CONSUMER_SECRET" in os.environ else "IfNlsgNrW5o6rfhayOURF1BcUDBcsrfgqss9g5inqeFytDbkgE"
access_token: str = os.getenv("TW_ACCESS_TOKEN") if \
    "TW_ACCESS_TOKEN" in os.environ else "973174862159253505-mAYpqjzegRXFNhdEPXOkDLsHWXePp7q"
access_token_secret: str = os.getenv("TW_ACCESS_TOKEN_SECRET") if\
    "TW_ACCESS_TOKEN_SECRET" in os.environ else "0mmfQcNDJBIFhMM9bexZSO1eIKhFdaP8JX9cMnBG81gJE"


def init_threads():
    global offline_threads
    offline_threads = []


def download_ner_models_background():
    if ner_library == "flair":
        logger.info("Downloading NER models for Flair ... ")
        download_ner_models()





