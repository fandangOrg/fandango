from helper import config as cfg
from models.article import Article
from json import loads
from managers.kafka_connector import KafkaConnector
from managers.elasticsearch_connector import ElasticsearchManager
from managers.neo4j_connector import NEO4JConnector
from managers.graph_analysis_connector import GraphAnalysis


class DataManager:
    def __init__(self, service):
        self.service = service
        self.graph_analysis_manager = None
        # Kafka Parameters
        self.topic_consumer = cfg.topic_consumer
        self.topic_producer = cfg.topic_producer
        self.group_id = cfg.group_id
        self.kafka_server = cfg.kafka_server
        self.enable_auto_commit = False
        self.timeout = 3000
        self.auto_offset_reset = "earliest"
        self.kafka_manager = None

        # Elasticsearch Parameters
        self.es_port = cfg.es_port
        self.es_host = cfg.es_host
        self.elasticsearch_manager = None

        # Neo4j Parameters
        self.neo4j_manager = None
        self.neo4j_host = cfg.neo4j_host
        self.neo4j_port = cfg.neo4j_port
        self.neo4j_username = cfg.neo4j_username
        self.neo4j_password = cfg.neo4j_password
        self.neo4j_protocol = cfg.protocol

    def init_kafka_manager(self):
        try:
            self.kafka_manager = KafkaConnector(topic_consumer=self.topic_consumer,
                                                topic_producer=self.topic_producer,
                                                group_id=self.group_id,
                                                bootstrap_servers=[self.kafka_server],
                                                enable_auto_commit=self.enable_auto_commit,
                                                consumer_timeout_ms=self.timeout,
                                                auto_offset_reset=self.auto_offset_reset)
            self.kafka_manager.init_kafka_consumer()
            self.kafka_manager.init_kafka_producer()
        except Exception as e:
            cfg.logger.error(e)
        return self

    def init_elasticsearch_manager(self):
        try:
            self.elasticsearch_manager = ElasticsearchManager(host=self.es_host, port=self.es_port)
            if not self.elasticsearch_manager.connection:
                self.elasticsearch_manager.connect()
        except Exception as e:
            cfg.logger.error(e)
            self.elasticsearch_manager = None
        return self

    def init_neo4j_manager(self):
        try:
            self.neo4j_manager = NEO4JConnector(host=self.neo4j_host, port=self.neo4j_port,
                                                username=self.neo4j_username, password=self.neo4j_password,
                                                protocol=self.neo4j_protocol)
            if not self.neo4j_manager.connection:
                self.neo4j_manager.connect_to_neo4j_graph()
        except Exception as e:
            cfg.logger.error(e)
        return self

    def init_graph_analysis(self):
        try:
            if self.elasticsearch_manager is None:
                self.init_elasticsearch_manager()
            if self.neo4j_manager is None:
                self.init_neo4j_manager()

            self.graph_analysis_manager = GraphAnalysis(neo4j_connector=self.neo4j_manager,
                                                        elasticsearch_connector=self.elasticsearch_manager)
        except Exception as e:
            cfg.logger.error(e)
        return self

    def execute_graph_analysis(self, document):
        response = None
        try:
            if self.graph_analysis_manager is None:
                self.init_graph_analysis()

            # Convert to Document
            if isinstance(document, dict):
                art_doc = Article()
                final_document = art_doc.article_from_dict(data=document)
            else:
                final_document = document
            response = self.graph_analysis_manager.apply_graph_analysis(document=final_document)
        except Exception as e:
            cfg.logger.error(e)
        return response

    def get_ratings_from_identifiers(self, index, identifiers, key):
        response = {"ratings": []}
        try:
            # Init Elasticsearch Manager
            if self.elasticsearch_manager is None:
                self.init_elasticsearch_manager()
            # Get the ratings given a set of ids
            for uuid in identifiers:
                response_es = self.elasticsearch_manager.retrieve_data_from_index_by_id(index, uuid)
                if response_es:
                    # TODO: RETRIEVE SCORE
                    response["ratings"].append(str(response_es[key]))
                else:
                    cfg.logger.warning("Element not found in Elasticsearch!")
        except  Exception as e:
            cfg.logger.error(e)
        return response

    def start_offline_process(self):
        done = True
        while done:
            try:
                self.kafka_manager.consumer.poll()
                for msg in self.kafka_manager.consumer:
                    try:
                        cfg.logger.info('Loading Kafka Message')
                        document = loads(msg.value)
                        cfg.logger.info('Executing Graph Analysis')
                        published_document = self.execute_graph_analysis(document=document)
                        if published_document is not None:
                            cfg.logger.info('Putting authors/publisher scores into Kafka')
                            self.kafka_manager.put_data_into_topic(data=published_document)
                            self.kafka_manager.consumer.commit()
                            cfg.logger.info('Done!')
                        else:
                            cfg.logger.warning("Author/Publisher score not ingested into Kafka")
                    except Exception as e:
                        cfg.logger.error(e)
                        self.kafka_manager.consumer.commit()
                        continue
            except Exception as e:
                cfg.logger.warning(e)
                continue
        return self

    def execute_source_domain_analysis(self, full_domain):
        response = {}
        try:
            if self.graph_analysis_manager is None:
                self.init_graph_analysis()
            response = self.graph_analysis_manager.analyse_publisher_ui(full_domain=full_domain)
        except Exception as e:
            cfg.logger.error(e)
        return response