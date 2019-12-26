import time
import pandas as pd
from threading import Thread
from helper import helper
from helper import global_variables as gv
from helper.kafka_connector import KafkaConnector
from preprocessing.preprocessing import FandangoPreprocesing
from models.article import Article


def execute_service(header_serv, topic_consumer, topic_producer, group_id, kafka_server, es_host, es_port,
                    timeout=3000,enable_auto_commit=False):
    try:
        gv.logger.info('Executing %s Service for pre-processing', header_serv)
        msg = "FANDANGO Processing Articles ..."
        if gv.thread is None:
            gv.service = header_serv
            kafka = KafkaConnector(topic_consumer,
                                   topic_producer,
                                   group_id,
                                   bootstrap_servers=[kafka_server],
                                   enable_auto_commit=enable_auto_commit,
                                   consumer_timeout_ms=timeout,
                                   msg=msg,
                                   service=header_serv)

            if (kafka.consumer is not None):
                gv.thread = Thread(target=kafka.get_data_from_topic_preprocess)
                gv.thread.start()

        output = get_status(es_host, es_port, kafka_server)

    except Exception as e:
        gv.logger.error(e)
        output = get_status(es_host, es_port, kafka_server)
        output['error'] = str(e)
    return output


def execute_preprocess_article(article_json):
    try:
        raw_data_df = pd.DataFrame.from_dict({0: article_json}, orient='index')

        preprocess = FandangoPreprocesing(raw_data_df, newspapers_list=gv.newspaper)
        ok = preprocess.run()

        if ok:
            # Get the article
            article = preprocess.total_cleaned_data
            # Generate output
            article_obj = Article(article)

            gv.logger.info('Article %s was preprocessed On %s', article_obj.identifier,
                           helper.get_datetime())
            return article_obj.to_dict_KAFKA()
        else:
            return {"error":"Bad request not text in article"}
    except Exception as e:
        gv.logger.error(e)
        return {"error": "Bad Request"}


def get_status(es_host,es_port,kafka_server):
    response = {"logs": [], "services": [], "time": time.time(), "externals": [
        {"name": "Elastic search", "running": helper.elastic_running(es_host, es_port), "icon": "elastic.png"},
        {"name": "Kafka", "running": helper.kafka_running("David", kafka_server), "icon": "kafka.png"}]}
    try:
        with open(gv.log_file_name, 'r') as log_file:
            response['logs'] = helper.tail(log_file, 10)
    except Exception:
        response['logs'] = ''
    response['ready'] = response['externals'][0]['running'] and response['externals'][1]['running']
    response['services'].append(
        {"name": "Preprocessing Batch Service", "read": "input_raw", "write": "input_preprocess", "status": "0",
         "service": "preprocess", "type": "batch"})
    response['services'].append(
        {"name": "Preprocessing Stream Service", "read": "input_raw", "write": "input_preprocess", "status": "0",
         "service": "preprocess", "type": "stream"})

    if gv.thread is not None:
        if gv.service == "streaming":
            response['services'][1]['status'] = 1
        elif gv.service == "batch":
            response['services'][0]['status'] = 2
        elif gv.service == None:
            response['services'][1]['status'] = 2

    return response