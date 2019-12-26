# -*- coding: utf-8 -*-
from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps
from preprocessing.preprocessing import FandangoPreprocesing
import pandas as pd
from helper import global_variables, elastic_connector, helper
from models.article import Article
from helper.helper import save_last_article

# =====================================================================
# ------------------------- Kafka Connector ---------------------------
# =====================================================================

class KafkaConnector:
    def __init__(self, topic_consumer, topic_producer, group_id,
                 bootstrap_servers=None, enable_auto_commit=False,
                 consumer_timeout_ms=1000, msg="", service="batch"):

        self.topic_consumer = topic_consumer
        self.topic_producer = topic_producer
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.service=service
        self.auto_offset_reset = "earliest"
        self.enable_auto_commit = enable_auto_commit
        self.consumer_timeout_ms = consumer_timeout_ms
        self.consumer = None
        self.producer = None
        self.msg = {"msg": msg}
        try:
            self.consumer = KafkaConsumer(self.topic_consumer,
                                          group_id=self.group_id,
                                          bootstrap_servers=self.bootstrap_servers,
                                          auto_offset_reset=self.auto_offset_reset,
                                          enable_auto_commit=self.enable_auto_commit)

            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                          value_serializer=lambda x: dumps(x).encode('utf-8'))

            self.elastic = elastic_connector.ElasticSearchConnector(global_variables.es_host,
                                                                    global_variables.es_port)
            self.elastic.connect()
        except Exception as e:
            global_variables.logger.error(e)
            self.msg = {"msg": getattr(e, "message", str(e))}

    def get_data_from_topic_preprocess(self):
        ok = {}
        done = True
        while done:
            try:
                self.consumer.poll()
                for msg in self.consumer:
                    try:
                        global_variables.logger.info('Loading Kafka Message')
                        data = loads(msg.value)
                        if 'identifier' in list(data.keys()):
                            df = pd.DataFrame.from_dict({0: data}, orient='index')
                            ok = {"success": self.preprocess_call(df)}
                            self.consumer.commit()
                        else:
                            global_variables.logger.warning('The document received does not contain an identifier.')
                    except Exception as e:
                        global_variables.logger.error(e)
                        self.consumer.commit()
                        continue
            except Exception as e:
                global_variables.logger.warning(e)
                continue
        return ok

    def put_data_into_topic(self, data):
        ok = True
        try:
            # Check if exists
            self.producer.send(topic=self.topic_producer, value=data)
        except Exception as e:
            global_variables.logger.error(e)
            ok = False
        return ok

    def preprocess_call(self, raw_data_df):
        response = {"error": False, "clean_data": {}}
        try:
            if not raw_data_df.empty:
                # PRE-PROCESSING STEP
                preprocess = FandangoPreprocesing(raw_data_df, newspapers_list=global_variables.newspaper)
                ok = preprocess.run()
                if ok:
                    article = preprocess.total_cleaned_data
                    # Create article object
                    article_kafka = Article(article)
                    global_variables.logger.info('Article %s was preprocessed On %s', article_kafka.identifier,
                                   helper.get_datetime())
                    try:
                        final_data = article_kafka.to_dict_KAFKA()
                        if final_data:
                            ok = self.put_data_into_topic(final_data)
                    except Exception as e:
                        global_variables.logger.warning('The article is empty and it will not be ingested into the queue.')

                    response['clean_data'] = str(ok)

        except Exception as e:
            global_variables.logger.error(e)
            response["error"] = getattr(e, "message", str(e))
        return response