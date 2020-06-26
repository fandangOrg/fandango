# -*- coding: utf-8 -*-
from kafka import KafkaConsumer, KafkaProducer
from json import dumps
from helper import global_variables as gv
from typing import Optional

# =====================================================================
# ------------------------- Kafka Connector ---------------------------
# =====================================================================


class KafkaConnector:
    def __init__(self, topic_consumer, topic_producer, group_id,
                 bootstrap_servers=None, enable_auto_commit=False,
                 consumer_timeout_ms=1000, auto_offset_reset="earliest"):

        self.topic_consumer: str = topic_consumer
        self.topic_producer: str = topic_producer
        self.group_id: str = group_id
        self.bootstrap_servers = bootstrap_servers
        self.enable_auto_commit: bool = enable_auto_commit
        self.consumer_timeout_ms: int = consumer_timeout_ms
        self.auto_offset_reset: str = auto_offset_reset
        self.connection: bool = False
        self.consumer: Optional[KafkaConsumer] = None
        self.producer: Optional[KafkaProducer] = None

    def init_kafka_consumer(self):
        self.connection: bool = False
        try:
            self.consumer: KafkaConsumer = KafkaConsumer(self.topic_consumer,
                                                         group_id=self.group_id,
                                                         bootstrap_servers=self.bootstrap_servers,
                                                         auto_offset_reset=self.auto_offset_reset,
                                                         enable_auto_commit=self.enable_auto_commit)
            self.connection: bool = True
        except ConnectionError as ce:
            gv.logger.error(ce)
        except Exception as e:
            gv.logger.error(e)

    def init_kafka_producer(self):
        self.connection: bool = False
        try:
            self.producer: KafkaProducer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                                         value_serializer=lambda x: dumps(x).encode('utf-8'))
            self.connection: bool = True
        except ConnectionError as ce:
            gv.logger.error(ce)
        except Exception as e:
            gv.logger.error(e)

    def put_data_into_topic(self, data: dict):
        try:
            if self.producer is not None:
                self.producer.send(topic=self.topic_producer, value=data)

        except ConnectionError as ce:
            gv.logger.error(ce)
            self.connection: bool = False
        except Exception as e:
            gv.logger.error(e)
