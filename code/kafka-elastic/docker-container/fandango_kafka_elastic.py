
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import time
import json
import os
import sys
import global_variables as gv
import custom_logger



def main():

    # INITIALIZE THE LOGGER INSTANCE
    logger = custom_logger.init_logger(__name__, gv.LOG_TYPE, gv.CONSOLE_LOG_LEVEL, gv.LOG_EXPIRATION_TIME)

    # CHECK SOME INPUT PARAMETERS
    if  gv.KAFKA_TOPIC == '' or \
        gv.KAFKA_CONSUMER_GROUP == '' or \
        gv.INPUT_JSON_ID_FIELD_PATH == '' or \
        gv.ES_INDEX_NAME == '' or \
        gv.ES_DOC_TYPE == '':

        logger.error('Empty input parameters have been found, the program will be closed...')
        return

    # DEFINING THE FIELDS/SUBFILEDS LIST USED TO FIND THE IDENTIFIER IN THE DATA SCHEMA
    try:
        path_to_id_field = list()
        for field in gv.INPUT_JSON_ID_FIELD_PATH.split(';'):
            field_name = field.lstrip().rstrip()
            if field_name == '':
                continue

            path_to_id_field.append(field_name)

        if len(path_to_id_field) < 1:
            logger.error('Schema path to the identifier in the data schema not found {0}, the program will be closed...'.format(path_to_id_field))
            return

    except Exception as e:
        logger.error(e)
        return


    # CREATE KAFKA CONSUMER INSTANCE
    consumer = KafkaConsumer(gv.KAFKA_TOPIC,
                            group_id=gv.KAFKA_CONSUMER_GROUP,
                            auto_offset_reset='earliest',
                            enable_auto_commit=gv.KAFKA_AUTOCOMMIT,
                            bootstrap_servers=[gv.KAFKA_HOST + ':' + str(gv.KAFKA_PORT)])

    logger.info('--> Kakfa Consumer object created')
    # logger.info(type(consumer))
    # logger.info(consumer)
    # logger.info(consumer.assignment())
    # logger.info(consumer.subscription())
    # logger.info(consumer.metrics())

    # CREATE ELASTICSEARCH INSTANCE
    es = Elasticsearch([{'host': gv.ES_HOST, 'port': gv.ES_PORT}])
    logger.info('--> Elasticsearch object created')


    # INITIAL CHECK OF EXTERNAL CONNECTIONS (KAFKA AND ES)
    if not verify_external_connections(consumer, es, logger):
        logger.error('Exiting from the program because of external connection problems...')
        return


    # HERE THE EXTERNAL CONNECTIONS (KAFKA AND ELASTICSEARCH) HAVE BEEN CHECKED AND ARE ALIVE

    topics = consumer.topics()
    logger.info(type(topics))
    logger.info('All Kafka topics available:')
    logger.info(topics)


    if gv.KAFKA_TOPIC not in topics:
        logger.error('Exiting from the program because the specified topic does not exist in Kafka...')
        return


    logger.info('GENERAL INFORMATION:')
    logger.info('KAFKA_TOPIC: ' + gv.KAFKA_TOPIC)
    logger.info('KAFKA_CONSUMER_GROUP: ' + gv.KAFKA_CONSUMER_GROUP)
    logger.info('INPUT_JSON_ID_FIELD_PATH: ' + str(path_to_id_field)[1:-1])
    logger.info('ES_INDEX_NAME: ' + gv.ES_INDEX_NAME)
    logger.info('ES_DOC_TYPE: ' + gv.ES_DOC_TYPE)


    logger.info('===============================================================')
    logger.info('  WAITING FOR DATA FROM KAFKA TO BE INSERTED IN ELASTICSEARCH')
    logger.info('===============================================================')

    loop = True

    while loop:

        try:
            # CHECK OF EXTERNAL CONNECTIONS (KAFKA AND ES) AFTER EACH LOOP CYCLE (ACTUALLY AT THE BEGINNING AND IF
            # ANY EXCEPTION OCCURRED BELOW)
            if not verify_external_connections(consumer, es, logger):
                # EXIT
                logger.error('Exiting from the program because of external connection problems...')
                loop = False
            else:

                # GET MESSAGES FROM KAFKA
                for message in consumer:

                    if message == None or message == '':
                        consumer.commit()
                        continue

                    # GETTING NEXT ENTRY FROM KAFKA
                    logger.info('Getting next message from Kafka:')
                    # logger.info(message)
                    # logger.info(message.value)

                    # DECODING JSON MESSAGE FROM KAFKA -> entry
                    try:
                        entry = json.loads(message.value)
                    except json.decoder.JSONDecodeError:
                        logger.warning('--> Decoding JSON has failed, skipping...')
                        consumer.commit()
                        continue

                    logger.debug(entry)
                        
                    # GETTING THE ENTRY IDENTIFIER (TO BE USED AS ELASTICSEARCH ID)
                    skip_element = False
                    es_id = ""
                    
                    for field in path_to_id_field:
                        if field in entry:
                            es_id = entry[field]
                        else:
                            logger.warning('--> The specified identifier field ({0}) not present in the element, skipping...'.format(str(path_to_id_field)[1:-1]))
                            consumer.commit()
                            skip_element = True
                            break


                    if skip_element or es_id == "" or es_id == None:
                        continue
                    

                    # UPSERT ENTRY IN ES
                    logger.info('Inserting entry in Elasticsearch with identifier: {0}'.format(es_id))
                    result = es.index(index=gv.ES_INDEX_NAME, doc_type=gv.ES_DOC_TYPE, id=es_id, body=entry)
                    logger.info(result)

                    if 'result' in result:
                        if result['result'] == 'created' or result['result'] == 'updated':
                            logger.info('--> Element upserted correctly in Elasticsearch, committing offset to Kafka...')
                        else:
                            logger.warning('--> Element with identifier {0} not upserted correctly in Elasticsearch...'.format(es_id))
                    else:
                        logger.warning('--> Upsertion failed on element with identifier {0}'.format(es_id))


                    consumer.commit()
                    # time.sleep(0.05)  # 50 ms

        except Exception as e:
            logger.warning(e)



    logger.info('===============================================================')
    logger.info('Closing the program...')
    logger.info('GENERAL INFORMATION OF THE EXECUTION:')
    logger.info('KAFKA_TOPIC: ' + gv.KAFKA_TOPIC)
    logger.info('KAFKA_CONSUMER_GROUP: ' + gv.KAFKA_CONSUMER_GROUP)
    logger.info('INPUT_JSON_ID_FIELD_PATH: ' + str(path_to_id_field)[1:-1])
    logger.info('ES_INDEX_NAME: ' + gv.ES_INDEX_NAME)
    logger.info('ES_DOC_TYPE: ' + gv.ES_DOC_TYPE)

    time.sleep(2) # 2 seconds

    if loop:
        # Commit any pending offsets before closing the consumer connection
        consumer.commit()
        time.sleep(2) # 2 seconds

        # Close down consumer
        consumer.close()

    logger.info('Program closed.')




def verify_external_connections(kafka_consumer, es, logger):

    kafka_connections_check = False
    es_connection_check = False

    logger.info('===============================================================')
    logger.info('EXTERNAL CONNECTIONS VERIFICATION:')

    if kafka_consumer is not None and kafka_consumer.topics() is not None:
        logger.info('Connected to Kafka at \'{0}:{1}\''.format(gv.KAFKA_HOST, gv.KAFKA_PORT))
        kafka_connections_check = True
    else:
        logger.error("No Kafka topics available, the connection to Kafka at \'{0}:{1}\' will be closed".format(gv.KAFKA_HOST, gv.KAFKA_PORT))
        kafka_consumer.close()


    if es is not None and es.ping(request_timeout=1):
        es_connection_check = True
        logger.info('Connected to ElasticSearch at \'{0}:{1}\''.format(gv.ES_HOST, gv.ES_PORT))
    else:
        logger.error('It was not possible to connect to Elasticsearch at \'{0}:{1}\''.format(gv.ES_HOST, gv.ES_PORT))

    logger.info('===============================================================')


    return kafka_connections_check and es_connection_check





if __name__ == '__main__':
    main()



