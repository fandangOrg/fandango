
import os


# GENERAL PARAMETERS

# docker container
LOG_TYPE = os.getenv('LOG_TYPE', 'BOTH')
CONSOLE_LOG_LEVEL = os.getenv('CONSOLE_LOG_LEVEL', 'DEBUG')
LOG_EXPIRATION_TIME = os.getenv('LOG_EXPIRATION_TIME', '2') # hours


# # local script
# LOG_TYPE = 'BOTH' # CONSOLE, FILES, BOTH or NONE
# CONSOLE_LOG_LEVEL = 'DEBUG'
# LOG_EXPIRATION_TIME = '2' # hours


#================================================

# KAFKA PARAMETERS

KAFKA_AUTOCOMMIT = False

# docker container
KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost')
KAFKA_PORT = os.getenv('KAFKA_PORT', '9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', '')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', '')
INPUT_JSON_ID_FIELD_PATH = os.getenv('INPUT_JSON_ID_FIELD_PATH', '')


# # local script
# KAFKA_HOST = 'localhost'
# KAFKA_PORT = '9092'
# KAFKA_TOPIC = 'input_raw'
# KAFKA_CONSUMER_GROUP = 'elastic_group'
# INPUT_JSON_ID_FIELD_PATH = 'identifier'


#================================================

# ELASTICSEARCH PARAMETERS

# docker container
ES_HOST = os.getenv('ES_HOST', 'localhost')
ES_PORT = os.getenv('ES_PORT', '9220')
ES_INDEX_NAME = os.getenv('ES_INDEX_NAME', '')
ES_DOC_TYPE = os.getenv('ES_DOC_TYPE', '')


# # local script
# ES_HOST = 'localhost'
# ES_PORT = '9220'
# ES_INDEX_NAME = 'test-kafka-es'
# ES_DOC_TYPE = 'doc'

