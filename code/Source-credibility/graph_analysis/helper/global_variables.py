# -*- coding: utf-8 -*-
import coloredlogs, logging
from queue import Queue
from threading import Event
import warnings, os
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)



# ====================================================================================
# ------------------------- GLOBAL VARIABLES Graph analysis---------------------------
# ====================================================================================

queue_neo4j = None
event = None


service = None

# Pre-processing Params
default_field: str = "Unknown"
org_default_field: str = "N/A"
ner_library: str = "spacy"

# Ports and Hosts
# Add environment variables
host: str = os.getenv("HOST_PORT") if "HOST_PORT" in os.environ else "0.0.0.0"
port: int = int(os.getenv("API_PORT")) if "API_PORT" in os.environ else 5000


# ====================================
# Elasticsearch environment variables
# ====================================

if os.getenv('ELASTICSEARCH_SERVER') is not None:
    es_host: str = os.getenv('ELASTICSEARCH_SERVER')
else:
    es_host: str = "localhost"

if os.getenv('ELASTICSEARCH_PORT') is not None:
    es_port: str = os.getenv('ELASTICSEARCH_PORT')
else:
    es_port: str = "9220"

if os.getenv('ELASTICSEARCH_INDEX_PER') is not None:
    person_es_index = os.getenv('ELASTICSEARCH_INDEX_PER')
else:
    person_es_index = "fdg-ap-person"

if os.getenv('ELASTICSEARCH_INDEX_ORG') is not None:
    org_es_index: str = os.getenv('ELASTICSEARCH_INDEX_ORG')
else:
    org_es_index: str = "fdg-ap-organization"

idf_es_index: str = "crawled-articles"
art_es_index: str = "fdg-textscore"

# ====================================
# Kafka environment variables
# ====================================

if os.getenv('KAFKA_SERVER') is not None:
    kf_host: str = os.getenv('KAFKA_SERVER')
else:
    kf_host: str = "localhost"

if os.getenv('KAFKA_PORT') is not None:
    kf_port: str = os.getenv('KAFKA_PORT')
else:
    kf_port: str = "9092"

if os.getenv('KAFKA_TOPIC_CONSUMER') is not None:
    topic_consumer: str = os.getenv('KAFKA_TOPIC_CONSUMER')
else:
    topic_consumer: str = 'input_preprocessed'

if os.getenv('KAFKA_TOPIC_PRODUCER') is not None:
    topic_producer: str = os.getenv('KAFKA_TOPIC_PRODUCER')
else:
    topic_producer: str = 'analyzed_auth_org'

kafka_server: str = kf_host + ":" + kf_port
group_id: str = 'upm_group'


# ====================================
# NEO4J environment variables
# ====================================

if os.getenv('NEO4J_HOST') is not None:
    neo4j_host: str = os.getenv('NEO4J_HOST')
else:
    neo4j_host: str = "localhost"

if os.getenv('NEO4J_PROTOCOL') is not None:
    protocol: str = os.getenv('NEO4J_PROTOCOL')
else:
    protocol: str = 'bolt'

if os.getenv('NEO4J_USERNAME') is not None:
    neo4j_username: str = os.getenv('NEO4J_USERNAME')
else:
    neo4j_username: str = "fandango"

if os.getenv('NEO4J_PASSWORD') is not None:
    neo4j_password: str = os.getenv('NEO4J_PASSWORD')
else:
    neo4j_password: str = "fandango"

# NEO4J Protocol
if protocol == 'bolt':
    neo4j_port: str = '7687'
elif protocol == 'http':
    neo4j_port: str = "7474" # "15005"
elif protocol == 'https':
    neo4j_port: str = '7473'

if os.getenv('FUSION_SCORE_SERVER') is not None:
    fusion_score_server: str = os.getenv('FUSION_SCORE_SERVER')
else:
    fusion_score_server: str = 'localhost'

if os.getenv('FUSION_SCORE_PORT') is not None:
    fusion_score_port: str = str(os.getenv('FUSION_SCORE_PORT'))
else:
    fusion_score_port: str = '10003'

if os.getenv('FUSION_SCORE_ENDPOINT') is not None:
    fusion_score_endpoint: str = os.getenv('FUSION_SCORE_ENDPOINT')
else:
    fusion_score_endpoint: str = 'api/fusion_score'


# ===========================================
offline_threads: list = []
neo4j_thread_name: str = "neo4j_thread"

# Process name
offline_service_name: str = "offline_service"
online_service_name: str = "online_service"
service_name: str = "Graph analysis"
error_msg: str = "An error occurred when applying pre-processing"
running_msg: str = "Running"
aborted_msg: str = "Aborted"

countries_websites: list = ["spain", "italy", "greece", "nl", "fr",
                            "belgium", "uk", "usa", "rus"]
resources_dir: str = "resources"
csv_filepath: str = "domains.csv"
xlsx_filepath: str = "domains.xlsx"
sheet_names_tld: list = ['country_tld', 'original_tld']
filepath_tld: str = "suffix_analysis.xlsx"
score_name: str = "trustworthiness"
centrality_rank_name: str = "centrality_rank"
anonymous_rank_name: str = "anonymous_rank"

logo_fandango: str = "data:image/jpeg;base64,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"


# HTTP RESPONSES
http_response_500: str = "Internal Server Error"
http_response_200: str = "Successful Operation"
http_response_422: str = "Invalid Input"
http_response_400: str = "Bad Request"
http_response_403: str = "HTTP Connection Error"
http_response_300: str = "Analysis in Progress"

# HTTP STATUS
status_done: int = 200
status_in_progress: int = 300
status_failed: int = 500


def init_threads():
    global offline_threads
    offline_threads = []


def init():
    """ Init method: Initialises the global variables required in the graph analysis
    """
    global event
    global queue_neo4j

    event = Event()
    queue_neo4j = Queue()

