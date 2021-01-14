import coloredlogs, logging
import warnings, os
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# ===============================================================
host: str = os.getenv("API_HOST") if "API_HOST" in os.environ else "localhost"
port: int = int(os.getenv("API_PORT")) if "API_PORT" in os.environ else 5003
es_host: str = os.getenv("ELASTICSEARCH_HOST") if "ELASTICSEARCH_HOST" in os.environ else "localhost"
es_port: str = os.getenv("ELASTICSEARCH_PORT") if "ELASTICSEARCH_PORT" in os.environ else "9220"

tweets_index_name: str = os.getenv("TWEETS_INDEX") if "TWEETS_INDEX" in os.environ else "tweets"
users_index_name: str = os.getenv("USERS_INDEX") if "USERS_INDEX" in os.environ else "users"

app_title: str = os.getenv("APP_TITLE") if "APP_TITLE" in os.environ else "TW-Streaming"
global_parent_dir: str = os.getenv("GLOBAL_PARENT_DIR") if "GLOBAL_PARENT_DIR" in os.environ else ""
consumer_key: str = os.getenv("TW_CONSUMER_KEY") if \
    "TW_CONSUMER_KEY" in os.environ else ""
consumer_secret: str = os.getenv("TW_CONSUMER_SECRET") if \
    "TW_CONSUMER_SECRET" in os.environ else ""
access_token: str = os.getenv("TW_ACCESS_TOKEN") if \
    "TW_ACCESS_TOKEN" in os.environ else ""
access_token_secret: str = os.getenv("TW_ACCESS_TOKEN_SECRET") if\
    "TW_ACCESS_TOKEN_SECRET" in os.environ else ""

botometer_api_key: str = os.getenv("BOTOMETER_API_KEY") if\
    "BOTOMETER_API_KEY" in os.environ else ""

mongo_host: str = os.getenv("MONGO_HOST") if\
    "MONGO_HOST" in os.environ else "localhost"
mongo_port: str = os.getenv("MONGO_PORT") if\
    "MONGO_PORT" in os.environ else "27017"

# ================================================================
base_url = f"http://{host}:{port}"
url_elastic_hq = "http://localhost:5000"
url_streaming_status = f"{base_url}/streaming/status"
url_streaming_form = f"{base_url}/streaming/form"
url_streaming_start = f"{base_url}//streaming/start"
url_streaming_stop = f"{base_url}/streaming/stop"
url_streaming_analytics = f"{base_url}/streaming/analytics"
# ================================================================


# =========================================================
global_streaming_threads: list = []
# =========================================================



