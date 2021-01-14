from helper.settings import logger, mongo_host, mongo_port, es_host, es_port, botometer_api_key
from helper.utils import read_all_files_from_local_storage
from tweepy import Status
from twitter_processors.fandango_twitter_data_processor import TwitterDataProcessor
from connectors.mongodb_connector import MongoDBConnector
from connectors.elasticsearch_connector import ElasticsearchConnector
from data_models.twitter_models import TwitterDataOutput
from connectors.twitter_api_connector import TwitterConnector


class SearchingProcessor(object):
    def __init__(self, twitter_connector: TwitterConnector, db_name: str,
                 collection_names: dict, local_storage: str,
                 dest_storage: str = "mongoDB", add_sentiment: bool = True,
                 add_bot_analysis: bool = True):
        self.twitter_connector: TwitterConnector = twitter_connector
        self.local_storage: str = local_storage
        self.dest_storage: str = dest_storage
        self.collection_names: dict = collection_names
        self.add_sentiment: bool = add_sentiment
        self.add_bot_analysis: bool = add_bot_analysis
        self.identifier_key: str = "uuid"
        self.mongodb_connector: MongoDBConnector = MongoDBConnector(
            host=mongo_host, port=mongo_port, db_name=db_name)
        self.elasticsearch_connector: ElasticsearchConnector = ElasticsearchConnector(
            host=es_host, port=es_port)
        self.set_up_storage_connection()

    def set_up_storage_connection(self):
        try:
            if self.dest_storage == "elasticsearch":
                self.elasticsearch_connector.connect()
            else:
                self.mongodb_connector.set_up_db()

        except Exception as e:
            logger.error(e)

    def get_twitter_credentials(self) -> dict:
        twitter_credentials: dict = {"consumer_key": self.twitter_connector.consumer_key,
                                     "consumer_secret": self.twitter_connector.consumer_secret,
                                     "access_token": self.twitter_connector.access_token,
                                     "access_token_secret": self.twitter_connector.access_token_secret,
                                     "botometer_api_key": botometer_api_key}
        return twitter_credentials

    def run_twitter_searching(self):
        try:
            # 1. Set up connection
            if self.twitter_connector.api is None:
                self.twitter_connector.set_up_twitter_api_connection()

            # 2. Run searching
            logger.info(f"Loading files from {self.local_storage}")
            data_tweets_ids: iter = read_all_files_from_local_storage(
                local_storage_path=self.local_storage, column_index=0)

            # 3. For each Tweet ID
            for tweet_id in data_tweets_ids:
                logger.info(f"1. Loading Status with ID {tweet_id}")

                # 3.1 Check if the data is already in the storage

                non_exists: bool = self.check_data_in_storage(
                    entity_id=tweet_id,
                    storage=self.dest_storage,
                    collection_name=self.collection_names.get("status"),
                    identifier_key="id")

                if non_exists:
                    logger.info(f"2. Pre-processing Status with ID {tweet_id}")
                    # 3.2 Retrieve Status
                    tweet_status: Status = TwitterConnector.get_tweet_data_from_tweet_id(
                        api=self.twitter_connector.api, tweet_id=tweet_id)

                    # If there is data
                    if tweet_status is not None:
                        # 3.3 Generate Output
                        output: TwitterDataOutput = TwitterDataProcessor.process_twitter_data(
                            tweet_status, add_sentiment=self.add_sentiment,
                            add_bot_analysis=self.add_bot_analysis,
                            twitter_credentials=self.get_twitter_credentials())

                        # Only insert if both elements are available
                        if output.status and output.user:
                            # 3.4 Store data
                            logger.info(f"3. Storing Status with ID {tweet_id} in {self.dest_storage.title()}")
                            self.storage_data(
                                data=output,
                                collection_names=self.collection_names,
                                storage=self.dest_storage,
                                mongodb_connector=self.mongodb_connector,
                                elasticsearch_connector=self.elasticsearch_connector,
                                identifier_key=self.identifier_key)
        except Exception as e:
            logger.error(e)

    def check_data_in_storage(self, entity_id: str, storage: str, collection_name: str,
                              identifier_key: str) -> bool:
        non_exist: bool = False
        try:
            if storage == "elasticsearch":
                uuid: str = SearchingProcessor.get_es_uuid_from_entity_id(
                    elasticsearch_connector=self.elasticsearch_connector,
                    entity_id=entity_id)
                non_exist: bool = self.elasticsearch_connector.check_document_in_index_by_id(
                    uuid=uuid, index=collection_name)
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

            # Insert User
            res_user: dict = elasticsearch_connector.bulk_data_into_index(
                index=collection_names.get("user"),
                uuid=data.user.get("uuid"),
                source_data=data.user)

            if res_status and res_user:
                logger.info("Inserted data into ES with success!")
        else:
            raise ValueError("JSON Storage Not Implemented yet")

    @staticmethod
    def get_es_uuid_from_entity_id(elasticsearch_connector: ElasticsearchConnector,
                                   entity_id: str):
        return elasticsearch_connector.generate_128_uuid_from_string(data_uuid=str(entity_id))