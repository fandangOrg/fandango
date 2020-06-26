# -*- coding: utf-8 -*-
from kafka import KafkaConsumer, KafkaProducer
from json import dumps
from helper import global_variables as gv
import os

# =====================================================================
# ------------------------- Kafka Connector ---------------------------
# =====================================================================


class KafkaConnector:
    def __init__(self, topic_consumer, topic_producer, group_id,
                 bootstrap_servers=None, enable_auto_commit=False,
                 consumer_timeout_ms=1000, auto_offset_reset="earliest"):

        self.topic_consumer = topic_consumer
        self.topic_producer = topic_producer
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.enable_auto_commit = enable_auto_commit
        self.consumer_timeout_ms = consumer_timeout_ms
        self.auto_offset_reset = auto_offset_reset
        self.consumer = None
        self.producer = None
        self.connection = False

    def init_kafka_consumer(self):
        try:
            self.consumer = KafkaConsumer(self.topic_consumer,
                                          group_id=self.group_id,
                                          bootstrap_servers=self.bootstrap_servers,
                                          auto_offset_reset=self.auto_offset_reset,
                                          enable_auto_commit=self.enable_auto_commit)

            self.connection = True
        except ConnectionError as ce:
            gv.logger.error(ce)
            self.connection = False
        except Exception as e:
            gv.logger.error(e)
            self.connection = False

    def init_kafka_producer(self):
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                          value_serializer=lambda x: dumps(x).encode('utf-8'))
            self.connection = True

        except ConnectionError as ce:
            gv.logger.error(ce)
            os._exit(0)
        except Exception as e:
            gv.logger.error(e)
            self.connection = False

    def put_data_into_topic(self, data):
        try:
            if self.producer is not None:
                self.producer.send(topic=self.topic_producer, value=data)

        except ConnectionError as ce:
            gv.logger.error(ce)
            os._exit(0)
        except Exception as e:
            gv.logger.error(e)
