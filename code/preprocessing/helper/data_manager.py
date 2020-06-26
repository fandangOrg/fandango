import sys
from models.article import Article
from json import loads
from helper import global_variables as gv
from models.preprocessing_models import PreprocessingOutputDocument
from helper.kafka_connector import KafkaConnector
from helper.elasticsearch_manager import ElasticsearchManager
from preprocessing.data_preprocessing import DataPreprocessing
from typing import Optional


class DataManager:
    def __init__(self, service):
        self.service: str = service
        self.data_preprocessing_manager: Optional[DataPreprocessing] = None

        # Kafka Parameters
        self.topic_consumer: str = gv.topic_consumer
        self.topic_producer: str = gv.topic_producer
        self.group_id: str = gv.group_id
        self.kafka_server: str = gv.kafka_server
        self.enable_auto_commit: bool = False
        self.timeout: int = 3000
        self.auto_offset_reset: str = "earliest"
        self.kafka_manager: Optional[KafkaConnector] = None

        # Elasticsearch Parameters
        self.es_port: str = gv.es_port
        self.es_host: str = gv.es_host
        self.elasticsearch_manager: Optional[ElasticsearchManager] = None

    def init_kafka_manager(self):
        try:
            if self.kafka_manager is None:
                self.kafka_manager: KafkaConnector = KafkaConnector(
                    topic_consumer=self.topic_consumer,
                    topic_producer=self.topic_producer,
                    group_id=self.group_id,
                    bootstrap_servers=[self.kafka_server],
                    enable_auto_commit=self.enable_auto_commit,
                    consumer_timeout_ms=self.timeout,
                    auto_offset_reset=self.auto_offset_reset)
                self.kafka_manager.init_kafka_consumer()
                self.kafka_manager.init_kafka_producer()

            if not self.kafka_manager.connection:
                gv.logger.error("Cannot connect to Kafka server at %s", str(self.kafka_server))
        except Exception as e:
            gv.logger.error(e)

    def init_elasticsearch_manager(self):
        try:
            if self.elasticsearch_manager is None:
                self.elasticsearch_manager: ElasticsearchManager = ElasticsearchManager(
                    host=self.es_host,
                    port=self.es_port)
            if self.elasticsearch_manager.es is None:
                self.elasticsearch_manager.connect()

            if not self.elasticsearch_manager.connection:
                gv.logger.error("Cannot cannot to Elasticsearch at %s:%s",
                                str(self.es_host), str(self.es_port))

        except Exception as e:
            gv.logger.error(e)
        return self

    def init_preprocessing(self):
        try:
            self.data_preprocessing_manager: DataPreprocessing = DataPreprocessing()
        except Exception as e:
            gv.logger.error(e)
        return self

    def execute_preprocessing(self, data, manual_annot: bool = False):
        output: PreprocessingOutputDocument = PreprocessingOutputDocument(
            message=gv.http_response_500, status=500)
        try:
            if self.data_preprocessing_manager is None:
                self.init_preprocessing()

            # Pre-process data
            output: PreprocessingOutputDocument = self.data_preprocessing_manager.apply_preprocessing(
                data=data,
                manual_annot=manual_annot)

            article_obj: Article = Article(data=output.data)
            article: dict = article_obj.article_to_dict()
            output.data: dict = article

        except Exception as e:
            gv.logger.error(e)
        return output

    def start_kafka_offline_process(self):
        done = True
        while done:
            try:
                self.kafka_manager.consumer.poll()
                for msg in self.kafka_manager.consumer:
                    try:
                        # 1. Load message from Kafka
                        gv.logger.info('Loading Kafka Message')
                        kafka_input_doc: dict = loads(msg.value)

                        # Response is correct
                        if kafka_input_doc.get("status", False) == 200:

                            gv.logger.info('Executing Preprocessing')
                            data: dict = kafka_input_doc["data"]

                            # 2. Execute Preprocessing
                            output: PreprocessingOutputDocument = self.execute_preprocessing(
                                data=data)

                            # 2.1 Everything was right
                            if output.status == 200:
                                kafka_output_doc: dict = output.dict_from_class()
                                if not self.data_preprocessing_manager.filter_news(output.data,
                                                                                   threshold=10,
                                                                                   col_key="articleBody"):

                                    gv.logger.info('Putting article into Kafka')
                                    self.kafka_manager.put_data_into_topic(data=kafka_output_doc)
                                    gv.logger.info('Done!')

                                self.kafka_manager.consumer.commit()

                            # 2.2 Possible errors
                            else:
                                gv.logger.warning("Article not ingested into Kafka.\nMessage: %s \nstatus %s",
                                                  output.message, output.status)
                    except ConnectionError as er:
                        gv.logger.error(er)
                        sys.exit(141)
                    except Exception as e:
                        gv.logger.error(e)
                        continue
            except Exception as e:
                gv.logger.warning(e)
                continue

    def start_experimental_kafka_process(self):
        done = True
        while done:
            try:
                self.kafka_manager.consumer.poll()
                for msg in self.kafka_manager.consumer:
                    try:
                        gv.logger.info('Loading Kafka Message')
                        data = loads(msg.value)
                        gv.logger.info('Executing Pre-processing')
                        # 2. Execute Preprocessing
                        output: PreprocessingOutputDocument = self.execute_preprocessing(
                            data=data)

                        # 2.1 Everything was right
                        if output.status == 200:

                            if not self.data_preprocessing_manager.filter_news(output.data,
                                                                               threshold=10,
                                                                               col_key="articleBody"):

                                gv.logger.info('Putting article into Temporal ES index')
                                res = self.elasticsearch_manager.bulk_data_into_index(
                                    index=gv.temp_es_index,
                                    uuid=output.data["identifier"],
                                    source_data=output.data)
                                if res:
                                    self.kafka_manager.consumer.commit()
                                    gv.logger.info('Done!')
                        else:
                            gv.logger.warning("Article not ingested into Kafka.\nMessage: %s \nstatus %s",
                                              output.message, output.status)
                    except Exception as e:
                        gv.logger.error(e)
                        continue
            except Exception as e:
                gv.logger.warning(e)
                continue