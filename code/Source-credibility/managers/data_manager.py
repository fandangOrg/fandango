import sys
from helper import global_variables as gv
from models.article import Article
from json import loads
from managers.kafka_connector import KafkaConnector
from managers.elasticsearch_connector import ElasticsearchManager
from managers.neo4j_connector import NEO4JConnector
from managers.graph_analysis_connector import GraphAnalysis
from models.graph_models import GraphAnalyzerOutputDoc
from typing import Optional
from kafka.errors import CommitFailedError


class DataManager:
    def __init__(self, service: str):
        self.service: str = service
        self.graph_analysis_manager: Optional[GraphAnalysis] = None

        # Kafka Parameters
        self.topic_consumer: str = gv.topic_consumer
        self.topic_producer: str = gv.topic_producer
        self.group_id: str = gv.group_id
        self.kafka_server: str = gv.kafka_server
        self.enable_auto_commit: bool = False
        self.auto_offset_reset: str = "earliest"
        self.kafka_manager: Optional[KafkaConnector] = None

        # Elasticsearch Parameters
        self.es_port: str = gv.es_port
        self.es_host: str = gv.es_host
        self.elasticsearch_manager: Optional[ElasticsearchManager] = None

        # Neo4j Parameters
        self.neo4j_manager: Optional[NEO4JConnector] = None
        self.neo4j_host = gv.neo4j_host
        self.neo4j_port = gv.neo4j_port
        self.neo4j_username = gv.neo4j_username
        self.neo4j_password = gv.neo4j_password
        self.neo4j_protocol = gv.protocol

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
                gv.logger.error("Cannot connect to Kafka server at %s", str(self.kafka_server))

        except Exception as e:
            gv.logger.error(e)

    def verify_kafka_connection(self):
        try:
            # 1. Init Manager
            if self.kafka_manager is None:
                self.init_kafka_manager()
            # 2. Verify Connection
            response_kafka: dict = self.kafka_manager.verify_kafka_connection()
            #
            if response_kafka.get("status", 400) != 200:
                gv.logger.error("Cannot connect to Kafka server at %s",
                                str(self.kafka_server))
        except Exception as e:
            gv.logger.error(e)

    def init_elasticsearch_manager(self):
        try:
            self.elasticsearch_manager: ElasticsearchManager = ElasticsearchManager(
                host=self.es_host, port=self.es_port)

            if not self.elasticsearch_manager.connection:
                self.elasticsearch_manager.connect()

            if not self.elasticsearch_manager.connection:
                gv.logger.error("Cannot connect to Elasticsearch at %s:%s",
                                str(self.es_host), str(self.es_port))

        except Exception as e:
            gv.logger.error(e)
            self.elasticsearch_manager = None

    def init_neo4j_manager(self):
        try:
            self.neo4j_manager: NEO4JConnector = NEO4JConnector(
                host=self.neo4j_host, port=self.neo4j_port,
                username=self.neo4j_username, password=self.neo4j_password,
                protocol=self.neo4j_protocol)

            if not self.neo4j_manager.connection:
                self.neo4j_manager.connect_to_neo4j_graph()

            if not self.neo4j_manager.connection:
                gv.logger.error("Cannot connect to Neo4j at %s:%s",
                                str(self.neo4j_host), str(self.neo4j_port))

        except Exception as e:
            gv.logger.error(e)

    def init_graph_analysis(self):
        try:
            if self.elasticsearch_manager is None:
                self.init_elasticsearch_manager()
            if self.neo4j_manager is None:
                self.init_neo4j_manager()

            self.graph_analysis_manager: GraphAnalysis = GraphAnalysis(
                neo4j_connector=self.neo4j_manager,
                elasticsearch_connector=self.elasticsearch_manager)
        except Exception as e:
            gv.logger.error(e)

    def execute_graph_analysis(self, document: dict):
        response:  GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(message=gv.http_response_500,
                                                                   status=500)
        try:
            # 1. Verify Graph Analysis Manager
            if self.graph_analysis_manager is None:
                self.init_graph_analysis()
            if document.get("status", 0) == 200:
                # 2. Convert Dictionary to Article Document
                art_doc: Article = Article()
                input_doc: dict = document["data"]

                art_doc_obj: Article = art_doc.article_from_dict(data=input_doc)

                # 3. Apply Asynchronous Graph Analysis
                response: GraphAnalyzerOutputDoc = self.graph_analysis_manager.apply_graph_analysis(
                    document=art_doc_obj)
            else:
                response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(message=gv.http_response_400,
                                                                          status=400)
        except Exception as e:
            gv.logger.error(e)
        return response

    def get_ratings_from_identifiers(self, index: str, identifiers: list, key: str):
        response = {"ratings": []}
        try:
            # Init Elasticsearch Manager
            if self.elasticsearch_manager is None:
                self.init_elasticsearch_manager()
            # Get the ratings given a set of ids
            for uuid in identifiers:
                response_es = self.elasticsearch_manager.retrieve_data_from_index_by_id(index, uuid)
                if response_es:
                    response["ratings"].append(str(response_es[key]))
                else:
                    gv.logger.warning("Element not found in Elasticsearch!")
        except Exception as e:
            gv.logger.error(e)
        return response

    def get_object_from_elasticsearch(self, index: str, identifier: id):
        response: dict = {}
        try:
            response: dict = self.elasticsearch_manager.retrieve_data_from_index_by_id(
                index=index, uuid=identifier)
        except Exception as e:
            gv.logger.error(e)
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
                        gv.logger.info('Loading Kafka Message')
                        document: dict = loads(msg.value)

                        # 3. Commit document
                        self.kafka_manager.consumer.commit()

                        # 4. Execute Analysis
                        if document.get("status", 400) == 200:
                            gv.logger.info('Executing Source credibility')
                            response: GraphAnalyzerOutputDoc = self.execute_graph_analysis(
                                document=document)

                            # 4.1 Everything was fine
                            if response.status == 200:
                                output_doc: dict = response.dict_from_class()
                                gv.logger.info('Putting authors/publisher scores into Kafka')
                                self.kafka_manager.put_data_into_topic(data=output_doc)
                                gv.logger.info('Done!')

                    # Handle Connection Exception
                    except ConnectionError as er:
                        gv.logger.error(er)
                        sys.exit(1)

                    # Handle CommitFailedError Exception
                    except CommitFailedError as commitErr:
                        gv.logger.error("Not able to make a commit ..." + str(commitErr))
                        # restart kafka elements and go back to while loop
                        self.kafka_manager.consumer = None
                        self.kafka_manager.producer = None
                        # Go out of the for loop
                        break

                    # Handle any other Exception
                    except Exception as e:
                        gv.logger.error(e)
                        # Perform commit and continue with next message
                        self.kafka_manager.consumer.commit()
                        continue

            # Handle While loop exceptions
            except ConnectionError as er:
                gv.logger.error(er)
                sys.exit(1)
            except Exception as e:
                gv.logger.warning(e)
                self.kafka_manager.consumer = None
                self.kafka_manager.producer = None

    def execute_source_domain_analysis(self, full_domain):
        response = {}
        try:
            if self.graph_analysis_manager is None:
                self.init_graph_analysis()
            response = self.graph_analysis_manager.analyse_publisher_ui(full_domain=full_domain)
        except Exception as e:
            gv.logger.error(e)
        return response