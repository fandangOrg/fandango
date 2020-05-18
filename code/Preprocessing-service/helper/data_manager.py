import sys
from helper import config as cfg
from models.article import Article
from json import loads
from helper.kafka_connector import KafkaConnector
from helper.elasticsearch_manager import ElasticsearchConnector
from preprocessing.data_preprocessing import DataPreprocessing
from typing import Optional


class DataManager:
    def __init__(self, service):
        self.service = service
        self.data_preprocessing_manager = None

        # Kafka Parameters
        self.topic_consumer = cfg.topic_consumer
        self.topic_producer = cfg.topic_producer
        self.group_id = cfg.group_id
        self.kafka_server = cfg.kafka_server
        self.enable_auto_commit = False
        self.timeout = 3000
        self.auto_offset_reset = "earliest"
        self.kafka_manager: Optional[KafkaConnector] = None

        # Elasticsearch Parameters
        self.es_port = cfg.es_port
        self.es_host = cfg.es_host
        self.elasticsearch_manager: Optional[ElasticsearchConnector] = None

    def init_kafka_manager(self):
        try:
            if self.kafka_manager is None:
                self.kafka_manager = KafkaConnector(topic_consumer=self.topic_consumer,
                                                    topic_producer=self.topic_producer,
                                                    group_id=self.group_id,
                                                    bootstrap_servers=[self.kafka_server],
                                                    enable_auto_commit=self.enable_auto_commit,
                                                    consumer_timeout_ms=self.timeout,
                                                    auto_offset_reset=self.auto_offset_reset)
                self.kafka_manager.init_kafka_consumer()
                self.kafka_manager.init_kafka_producer()

            if not self.kafka_manager.connection:
                cfg.logger.error("Cannot connect to Kafka server at %s", str(self.kafka_server))
        except Exception as e:
            cfg.logger.error(e)

    def init_elasticsearch_manager(self):
        try:
            if self.elasticsearch_manager is None:
                self.elasticsearch_manager = ElasticsearchConnector(host=self.es_host,
                                                                    port=self.es_port)
            if self.elasticsearch_manager.es is None:
                self.elasticsearch_manager.connect()

            if not self.elasticsearch_manager.connection:
                cfg.logger.error("Cannot cannot to Elasticsearch at %s:%s",
                                 str(self.es_host), str(self.es_port))

        except Exception as e:
            cfg.logger.error(e)
        return self

    def init_preprocessing(self):
        try:
            self.data_preprocessing_manager = DataPreprocessing()
        except Exception as e:
            cfg.logger.error(e)
        return self

    def execute_preprocessing(self, data, manual_annot=False):
        article = None
        try:
            if self.data_preprocessing_manager is None:
                self.init_preprocessing()
            # Pre-process data
            cleaned_data = self.data_preprocessing_manager.apply_preprocessing(data=data,
                                                                               manual_annot=manual_annot)
            article = Article(cleaned_data)
        except Exception as e:
            cfg.logger.error(e)
        return article

    def start_kafka_process(self):
        done = True
        while done:
            try:
                self.kafka_manager.consumer.poll()
                for msg in self.kafka_manager.consumer:
                    try:
                        cfg.logger.info('Loading Kafka Message')
                        data = loads(msg.value)
                        cfg.logger.info('Executing Preprocessing')
                        article_obj = self.execute_preprocessing(data=data)
                        if article_obj is not None:
                            article = article_obj.article_to_dict()

                            # TODO: Add filter
                            if not self.data_preprocessing_manager.filter_news(article,
                                                                               threshold=10,
                                                                               col_key="articleBody"):

                                cfg.logger.info('Putting article into Kafka')
                                self.kafka_manager.put_data_into_topic(data=article)
                                self.kafka_manager.consumer.commit()
                                cfg.logger.info('Done!')
                        else:
                            cfg.logger.warning("Article not ingested into Kafka")

                    except ConnectionError as er:
                        print("1234")
                        cfg.logger.error(er)
                        sys.exit(141)
                    except Exception as e:
                        cfg.logger.error(e)
                        self.kafka_manager.consumer.commit()
                        continue
            except Exception as e:
                cfg.logger.warning(e)
                continue
        return self

    def start_experimental_kafka_process(self):
        done = True
        while done:
            try:
                self.kafka_manager.consumer.poll()
                for msg in self.kafka_manager.consumer:
                    try:
                        cfg.logger.info('Loading Kafka Message')
                        data = loads(msg.value)
                        cfg.logger.info('Executing Pre-processing')
                        article_obj = self.execute_preprocessing(data=data)
                        if article_obj is not None:
                            article = article_obj.article_to_dict()

                            # TODO: Add filter
                            if not self.data_preprocessing_manager.filter_news(article,
                                                                               threshold=10,
                                                                               col_key="articleBody"):

                                cfg.logger.info('Putting article into Temporal ES index')
                                res = self.elasticsearch_manager.bulk_data_into_index(index=cfg.temp_es_index,
                                                                                      uuid=article["identifier"],
                                                                                      source_data=article)
                                if res:
                                    self.kafka_manager.consumer.commit()
                                    cfg.logger.info('Done!')
                        else:
                            cfg.logger.warning("Article not ingested into Kafka")
                    except Exception as e:
                        cfg.logger.error(e)
                        self.kafka_manager.consumer.commit()
                        continue
            except Exception as e:
                cfg.logger.warning(e)
                continue
        return self


