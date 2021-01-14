# -*- coding: utf-8 -*-
import coloredlogs, logging
import warnings, os
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

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

score_art_es_index: str = os.getenv("TEXT_SCORE_ES_INDEX") if \
    "TEXT_SCORE_ES_INDEX" in os.environ else "fdg-textscore"
art_es_index: str = os.getenv("ARTICLE_ES_INDEX") if \
    "ARTICLE_ES_INDEX" in os.environ else "fdg-article"
org_es_index_features: str = os.getenv("ORG_FEATURES_ES_INDEX") if \
    "ORG_FEATURES_ES_INDEX" in os.environ else "fdg-organization-features"
auth_es_index_features: str = os.getenv("AUTH_FEATURES_ES_INDEX") if \
    "AUTH_FEATURES_ES_INDEX" in os.environ else "fdg-person-features"

os.environ['PARENT_DIR'] = "sourceRank"

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

# SourceRank Params
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
    "TW_ACCESS_TOKEN" in os.environ else "973174862159253505-q2tjHH7dE0x3ls7GAC3AGAsT4Bt2Ct2"
access_token_secret: str = os.getenv("TW_ACCESS_TOKEN_SECRET") if\
    "TW_ACCESS_TOKEN_SECRET" in os.environ else "6cYEgyyoe2vgKJuxWlRGKJyCNK2WB13NSwRcwRMVn0KNd"

botometer_api_key: str = os.getenv("BOTOMETER_API_KEY") if\
    "BOTOMETER_API_KEY" in os.environ else "81aa458198msh2b44caa14c0fd57p13f0e1jsn080f2818c023"

# Process name
offline_service_name: str = "offline_service"
online_service_name: str = "online_service"
service_name: str = "Source credibility analysis"
error_msg: str = "An error occurred when applying processing"
running_msg: str = "Running"
aborted_msg: str = "Aborted"
default_field: str = "N/A"

offline_threads: list = []
default_name: str = "Anonymous"
score_key: str = "trustworthiness"

# HTTP RESPONSES
http_response_500: str = "Internal Server Error"
http_response_200: str = "Successful Operation"
http_response_422: str = "Invalid Input"
http_response_400: str = "Bad Request"
http_response_403: str = "HTTP Connection Error"
http_response_300: str = "Analysis in Progress"
http_response_409: str = "Cannot connect to Elasticsearch"

# HTTP STATUS
status_done: int = 200
status_in_progress: int = 300
status_failed: int = 500

global_streaming_threads: list = []

# Swagger Information
ui_base_path: str = os.getenv("UI_BASE_PATH") if "UI_BASE_PATH" in os.environ else os.path.join(
    "", "docs")

static_folder: str = os.path.join(ui_base_path, "static")
templates_folder: str = os.path.join(ui_base_path, "templates")
swagger_template_file: str = 'swaggerui.html'
