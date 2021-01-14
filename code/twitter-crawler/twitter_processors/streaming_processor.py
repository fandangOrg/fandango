import sys
from urllib3.exceptions import ProtocolError
from helper.settings import (logger, mongo_host, mongo_port, es_host, es_port,
                             consumer_secret, consumer_key, access_token_secret,
                             access_token, botometer_api_key)
from tweepy import API, Stream, StreamListener, Status
from twitter_processors.twitter_data_processor import TwitterDataProcessor
from connectors.mongodb_connector import MongoDBConnector
from connectors.elasticsearch_connector import ElasticsearchConnector
from data_models.twitter_models import TwitterDataOutput


class StreamingProcessor(object):
    def __init__(self, api: API, languages: list, track: list, db_name: str,
                 collection_names: dict, storage: str = "mongoDB",
                 add_sentiment: bool = True, add_bot_analysis: bool = True):
        self.api: API = api
        self.languages: list = languages
        self.track: list = track
        self.tweet_mode: str = "extended"
        self.storage: str = storage
        self.collection_names: dict = collection_names
        self.add_sentiment: bool = add_sentiment
        self.add_bot_analysis: bool = add_bot_analysis

        self.mongodb_connector: MongoDBConnector = MongoDBConnector(
            host=mongo_host, port=mongo_port, db_name=db_name)
        self.elasticsearch_connector: ElasticsearchConnector = ElasticsearchConnector(
            host=es_host, port=es_port)
        self.set_up_storage_connection()
        self.stream_listener: TwitterStreamListener = TwitterStreamListener(
            storage=storage, collection_names=self.collection_names,
            mongodb_connector=self.mongodb_connector,
            elasticsearch_connector=self.elasticsearch_connector,
            add_sentiment=self.add_sentiment, add_bot_analysis=self.add_bot_analysis)

    def set_up_storage_connection(self):
        try:
            if self.storage == "elasticsearch":
                self.elasticsearch_connector.connect()
            else:
                self.mongodb_connector.set_up_db()

        except Exception as e:
            logger.error(e)
    
    def run_twitter_streaming(self):
        try:
            # Start streaming
            stream: Stream = Stream(
                auth=self.api.auth,
                listener=self.stream_listener,
                tweet_mode=self.tweet_mode)
            while True:
                try:
                    stream.filter(
                        languages=self.languages,
                        track=self.track,
                        stall_warnings=True, is_async=False)
                
                except (ProtocolError, AttributeError):
                    continue
                except Exception as e:
                    logger.error(e)
            stream.filter(languages=self.languages, track=self.track)
            
        except Exception as e:
            logger.error(e)
    

class TwitterStreamListener(StreamListener):
    def __init__(self, storage: str, collection_names: dict,
                 mongodb_connector: MongoDBConnector,
                 elasticsearch_connector: ElasticsearchConnector,
                 add_sentiment: bool = True, add_bot_analysis: bool = True):
        super().__init__()
        self.storage: str = storage
        self.collection_names: dict = collection_names
        self.add_sentiment: bool = add_sentiment
        self.add_bot_analysis: bool = add_bot_analysis
        self.mongodb_connector: MongoDBConnector = mongodb_connector
        self.elasticsearch_connector: ElasticsearchConnector = elasticsearch_connector
        self.identifier_key: str = "uuid"

    def on_status(self, status: Status):

        logger.info(f"1. Loading Status with ID {status.__getattribute__('id')}")

        # 1. Check whether the status is already in the storage
        non_exists: bool = self.check_data_in_storage(
            entity_id=status.__getattribute__('id'),
            storage=self.storage,
            collection_name=self.collection_names.get("status"),
            identifier_key="id")

        if non_exists:
            # 3. Process Tweets an Users
            logger.info(f"2. Pre-processing Status with ID {status.__getattribute__('id')}")
            data: TwitterDataOutput = self.process_status(
                status=status, add_sentiment=self.add_sentiment,
                add_bot_analysis=self.add_bot_analysis)

            logger.info(f"3. Storing Status with ID {status.__getattribute__('id')} in {self.storage.title()}")
            # 2. Storage data
            self.storage_data(data=data, collection_names=self.collection_names,
                              storage=self.storage, mongodb_connector=self.mongodb_connector,
                              elasticsearch_connector=self.elasticsearch_connector,
                              identifier_key=self.identifier_key)

    def on_error(self, status_code: int):
        if status_code == 420:
            logger.warning(f"Enhance Your Calm; The App is Being Rate Limited For Making Too Many Requests!\n")
            return False
        else:
            logger.error(f"Error {status_code} when ingesting a tweet\n")
            sys.exit()

    @staticmethod
    def get_twitter_credentials() -> dict:
        twitter_credentials: dict = {"consumer_key": consumer_key,
                                     "consumer_secret": consumer_secret,
                                     "access_token": access_token,
                                     "access_token_secret": access_token_secret,
                                     "botometer_api_key": botometer_api_key}
        return twitter_credentials

    @staticmethod
    def process_status(status: Status, add_sentiment=True, add_bot_analysis=True) -> TwitterDataOutput:
        response: TwitterDataOutput = TwitterDataProcessor.process_twitter_data(
            status=status, add_sentiment=add_sentiment,
            add_bot_analysis=add_bot_analysis,
            twitter_credentials=TwitterStreamListener.get_twitter_credentials())
        return response

    def check_data_in_storage(self, entity_id: str, storage: str, collection_name: str,
                              identifier_key: str) -> bool:
        non_exist: bool = False
        try:
            if storage == "elasticsearch":
                non_exist: bool = self.elasticsearch_connector.check_document_in_index_by_id(
                    uuid=entity_id, index=collection_name)
            else:
                non_exist: bool = self.mongodb_connector.check_document_in_collection_by_id(
                    entity_id=entity_id, collection_name=collection_name,
                    identifier_key=identifier_key)
        except Exception as e:
            logger.error(e)
        return non_exist

    @staticmethod
    def storage_data(data: TwitterDataOutput, collection_names: dict, storage: str,
                     mongodb_connector: MongoDBConnector,
                     elasticsearch_connector: ElasticsearchConnector,
                     identifier_key: str):

        if storage == "mongoDB":
            # 1. Insert Status
            non_exist_status: bool = mongodb_connector.verify_documents_in_collection(
                entity=data.status, collection_name=collection_names.get("status"),
                identifier_key=identifier_key)
            if non_exist_status:
                mongodb_connector.insert_document_to_collection(
                    document=data.status,
                    collection_name=collection_names.get("status"))

            # 2. Insert User
            non_exist_user: bool = mongodb_connector.verify_documents_in_collection(
                entity=data.user, collection_name=collection_names.get("user"),
                identifier_key=identifier_key)
            if non_exist_user:
                mongodb_connector.insert_document_to_collection(
                    document=data.user,
                    collection_name=collection_names.get("user"))

            logger.info("Inserted data into MongoDB with success!")

        elif storage == "elasticsearch":
            # Insert status
            res_status: dict = elasticsearch_connector.bulk_data_into_index(
                index=collection_names.get("status"),
                uuid=data.status.get("uuid"),
                source_data=data.status)
            print(res_status)

            # Insert User
            res_user: dict = elasticsearch_connector.bulk_data_into_index(
                index=collection_names.get("user"),
                uuid=data.user.get("uuid"),
                source_data=data.user)
            print(res_user)

            if res_status and res_user:
                logger.info("Inserted data into ES with success!")

    @staticmethod
    def get_es_uuid_from_entity_id(elasticsearch_connector: ElasticsearchConnector,
                                   entity_id: str):
        return elasticsearch_connector.generate_128_uuid_from_string(data_uuid=str(entity_id))

