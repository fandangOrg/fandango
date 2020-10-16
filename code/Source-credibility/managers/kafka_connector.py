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
                 auto_offset_reset="earliest", max_poll_records=3,
                 max_poll_interval_ms=600000,
                 session_timeout_ms=100000,
                 heartbeat_interval_ms=20000):

        self.topic_consumer: str = topic_consumer
        self.topic_producer: str = topic_producer
        self.group_id: str = group_id
        self.bootstrap_servers = bootstrap_servers
        self.enable_auto_commit: bool = enable_auto_commit
        self.auto_offset_reset: str = auto_offset_reset
        self.max_poll_records: int = max_poll_records
        self.max_poll_interval_ms: int = max_poll_interval_ms
        self.session_timeout_ms: int = session_timeout_ms
        self.heartbeat_interval_ms: int = heartbeat_interval_ms
        self.connection: bool = False
        self.consumer: Optional[KafkaConsumer] = None
        self.producer: Optional[KafkaProducer] = None

    def verify_kafka_connection(self):
        response: dict = {"status": 400,
                          "message": gv.http_response_400}
        try:
            self.connection = False
            self.init_kafka_consumer()
            if self.consumer is not None:
                topics = self.consumer.topics()
                if topics:
                    self.connection = True
                    response["status"] = 200
                    response["message"] = gv.http_response_200
                else:
                    gv.logger.error("No topics available, the connection to Kafka will be closed")
        except Exception as e:
            gv.logger.error(e)
        return response

    def init_kafka_consumer(self):
        self.connection: bool = False
        try:
            self.consumer: KafkaConsumer = KafkaConsumer(self.topic_consumer,
                                                         group_id=self.group_id,
                                                         bootstrap_servers=self.bootstrap_servers,
                                                         auto_offset_reset=self.auto_offset_reset,
                                                         enable_auto_commit=self.enable_auto_commit,
                                                         max_poll_records=self.max_poll_records,
                                                         max_poll_interval_ms=self.max_poll_interval_ms,
                                                         session_timeout_ms=self.session_timeout_ms,
                                                         heartbeat_interval_ms=self.heartbeat_interval_ms,
                                                         api_version=(2,))
            self.connection: bool = True
        except ConnectionError as ce:
            gv.logger.error(ce)
        except Exception as e:
            gv.logger.error(e)

    def init_kafka_producer(self):
        self.connection: bool = False
        try:
            self.producer: KafkaProducer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                                         value_serializer=lambda x: dumps(x).encode('utf-8'),
                                                         api_version=(2,))
            self.connection: bool = True
        except ConnectionError as ce:
            gv.logger.error(ce)
        except Exception as e:
            gv.logger.error(e)

    def put_data_into_topic(self, data: dict):
        try:
            if self.producer is not None:
                self.producer.send(topic=self.topic_producer, value=data)
                self.producer.flush()
        except ConnectionError as ce:
            gv.logger.error(ce)
            self.connection: bool = False
        except Exception as e:
            gv.logger.error(e)
