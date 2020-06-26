# -*- coding: utf-8 -*-

# ====================================================================================
# ------------------------- GLOBAL VARIABLES PREPROCESSING ---------------------------
# ====================================================================================

import os
from helper.custom_log import init_logger
from helper.country_information import country_domains

import warnings
warnings.filterwarnings('ignore')


log_file_name = os.path.join("app_logs", "app.log")
logger = None
thread = None
service = None
offline_threads: list = []
country_domains: dict = country_domains

# Pre-processing Params
default_field = 'Unknown'
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
    es_port = "9220"

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
    topic_consumer = 'input_raw_2'

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


def init_threads():
    global offline_threads
    offline_threads = []


def init_logging_obj():
    global logger
    logger = init_logger(__name__, testing_mode=False)
