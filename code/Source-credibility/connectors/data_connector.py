import sys
from helper.settings import (logger, topic_consumer, topic_producer,
                             group_id, kafka_server, es_port, es_host,
                             http_response_500)
from fandango_models.article import Article
from fandango_models.source_credibility_models import GraphAnalyzerOutputDoc
from json import loads
from connectors.kafka_connector import KafkaConnector
from connectors.elasticsearch_connector import ElasticsearchConnector
from connectors.source_credibility_connector import SourceCredibilityConnector
from typing import Optional
from kafka.errors import CommitFailedError


class DataConnector:
    def __init__(self, service: str):
        self.service: str = service

        # Kafka Parameters
        self.topic_consumer: str = topic_consumer
        self.topic_producer: str = topic_producer
        self.group_id: str = group_id
        self.kafka_server: str = kafka_server
        self.enable_auto_commit: bool = False
        self.auto_offset_reset: str = "earliest"
        self.kafka_manager: Optional[KafkaConnector] = None

        # Elasticsearch Parameters
        self.es_port: str = es_port
        self.es_host: str = es_host
        self.elasticsearch_connector: ElasticsearchConnector = ElasticsearchConnector(
            host=self.es_host, port=self.es_port)
        self.source_credibility_connector: SourceCredibilityConnector = SourceCredibilityConnector(
            elasticsearch_connector=self.elasticsearch_connector)

    def init_kafka_manager(self):
        try:
            self.kafka_manager: KafkaConnector = KafkaConnector(
                topic_consumer=self.topic_consumer,
                topic_producer=self.topic_producer,
                group_id=self.group_id,
                bootstrap_servers=[self.kafka_server],
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset=self.auto_offset_reset)
            self.kafka_manager.init_kafka_consumer()
            self.kafka_manager.init_kafka_producer()

            if not self.kafka_manager.connection:
                logger.error(f"Cannot connect to Kafka server at {self.kafka_server}")

        except Exception as e:
            logger.error(e)

    def verify_kafka_connection(self):
        try:
            # 1. Init Manager
            if self.kafka_manager is None:
                self.init_kafka_manager()
            # 2. Verify Connection
            response_kafka: dict = self.kafka_manager.verify_kafka_connection()
            #
            if response_kafka.get("status", 400) != 200:
                logger.error("Cannot connect to Kafka server at %s",
                                str(self.kafka_server))
        except Exception as e:
            logger.error(e)

    def init_elasticsearch_connector(self):
        try:
            if not self.elasticsearch_connector.connection:
                self.elasticsearch_connector.connect()

            if not self.elasticsearch_connector.connection:
                logger.error(f"Cannot connect to Elasticsearch at {self.es_host}:{self.es_port}")

        except Exception as e:
            logger.error(e)

    def process_source_credibility_analysis(self, document: dict) -> GraphAnalyzerOutputDoc:
        response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(message=http_response_500,
                                                                  status=500)
        try:
            if document.get("status", 0) == 200:
                # 1. Convert Dictionary to Article Document
                art_doc: Article = Article()
                input_doc: dict = document.get("data")

                # 2. Convert article to dict to verify fields
                art_doc_obj: Article = art_doc.article_from_dict(data=input_doc)

                # 3. Compute Trustworthiness process
                response: GraphAnalyzerOutputDoc = self.source_credibility_connector.apply_analysis(
                    document=art_doc_obj)

        except Exception as e:
            logger.error(e)
        return response

    def get_ratings_from_identifiers(self, index: str, identifiers: list, key: str):
        response = {"ratings": []}
        try:
            # Init Elasticsearch Manager
            if self.elasticsearch_connector is None:
                self.init_elasticsearch_connector()
            # Get the ratings given a set of ids
            for uuid in identifiers:
                response_es = self.elasticsearch_connector.retrieve_data_from_index_by_id(index, uuid)
                if response_es:
                    response["ratings"].append(str(response_es[key]))
                else:
                    logger.warning("Element not found in Elasticsearch!")
        except Exception as e:
            logger.error(e)
        return response

    def get_object_from_elasticsearch(self, index: str, identifier: id):
        response: dict = {}
        try:
            response: dict = self.elasticsearch_connector.retrieve_data_from_index_by_id(
                index=index, uuid=identifier)
        except Exception as e:
            logger.error(e)
        return response

    def start_kafka_offline_process(self):
        run: bool = True
        while run:
            try:
                # 1. Check if the consumer was initialised
                if self.kafka_manager.consumer is None:
                    self.kafka_manager.init_kafka_consumer()

                # 1. Check if the producer was initialised
                if self.kafka_manager.producer is None:
                    self.kafka_manager.init_kafka_producer()

                # 1. Read messages from Kafka
                for msg in self.kafka_manager.consumer:
                    try:
                        # 2. Process message
                        logger.info('Loading Kafka Message')
                        document: dict = loads(msg.value)

                        # 3. Commit document
                        self.kafka_manager.consumer.commit()

                        # 4. Execute Analysis
                        if document.get("status", 400) == 200:
                            logger.info('Executing Source credibility analysis')
                            response: GraphAnalyzerOutputDoc = self.process_source_credibility_analysis(
                                document=document)

                            # 4.1 Everything was fine
                            if response.status == 200:
                                output_doc: dict = response.__dict__
                                logger.info('Putting authors/publisher scores into Kafka')
                                self.kafka_manager.put_data_into_topic(data=output_doc)
                                logger.info('Done!')

                    # Handle Connection Exception
                    except ConnectionError as er:
                        logger.error(er)
                        sys.exit(1)

                    # Handle CommitFailedError Exception
                    except CommitFailedError as commitErr:
                        logger.error("Not able to make a commit ..." + str(commitErr))
                        # restart kafka elements and go back to while loop
                        self.kafka_manager.consumer = None
                        self.kafka_manager.producer = None
                        # Go out of the for loop
                        break

                    # Handle any other Exception
                    except Exception as e:
                        logger.error(e)
                        # Perform commit and continue with next message
                        self.kafka_manager.consumer.commit()
                        continue

            # Handle While loop exceptions
            except ConnectionError as er:
                logger.error(er)
                sys.exit(1)
            except Exception as e:
                logger.warning(e)
                self.kafka_manager.consumer = None
                self.kafka_manager.producer = None
