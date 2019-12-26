import json
import os
from flask import Flask, send_from_directory,request
from flask_cors import CORS
from services import preprocessing_services as serv
from helper import global_variables, helper


app = Flask(__name__,static_folder=os.path.join(os.getcwd(),'www'))
CORS(app)


# ======================================================================================================================
# ----------------------------------------------- PRE-PROCESSING SERVICES ----------------------------------------------
# ======================================================================================================================
@app.route('/', methods=['GET'])
def root():
    return app.send_static_file('index.html')

# ============================================================
# --------------------- Batch Service ------------------------
# ============================================================

@app.route('/preprocess/batch/start', methods=['GET', 'POST'])
def preprocessing_batch_service():
    header_serv = 'batch'
    topic_consumer = 'input_raw'
    topic_producer = 'input_preprocessed'
    group_id = 'upm_group'

    # -------------------------------------
    # ------------ DOCKER ----------------
    # os.system('./tunnel_kafka.sh')
    # --------------------------------------

    kafka_server = global_variables.kafka_server
    output = serv.execute_service(header_serv= header_serv,
                                  topic_consumer=topic_consumer,
                                  topic_producer=topic_producer,
                                  group_id= group_id,
                                  kafka_server=kafka_server,
                                  es_host=global_variables.es_host,
                                  es_port=global_variables.es_port)
    return json.dumps(output)


@app.route('/status', methods=['GET'])
def service_status():
    kafka_server = global_variables.kafka_server
    return json.dumps(serv.get_status(global_variables.es_host,
                                      global_variables.es_port,
                                      kafka_server))


@app.route('/preprocess/stream/start', methods=['GET'])
def preprocessing_streaming_service_stream():
    """
    This method gets the last message from a Kafka topic, applies preprocessing and
     generates an output with the proper format.
    :return:
        - output : JSON file with the data model from an article object.
    """

    header_serv = 'streaming'
    topic_consumer = 'input_raw'
    topic_producer = 'input_preprocessed'
    group_id = 'upm_group'
    kafka_server = global_variables.kafka_server
    output = serv.execute_service(header_serv=header_serv,
                                  topic_consumer=topic_consumer,
                                  topic_producer=topic_producer,
                                  group_id=group_id,
                                  kafka_server=kafka_server,
                                  es_host=global_variables.es_host,
                                  es_port=global_variables.es_port)
    return json.dumps(output)


@app.route('/preprocess/stream/stop', methods=['GET'])
def preprocessing_streaming_service_stop():
    kakfa_server = global_variables.kafka_server
    if global_variables.thread is not None:
        global_variables.service = None
    return json.dumps(serv.get_status(global_variables.es_host,
                                      global_variables.es_port,
                                      kakfa_server))


@app.route('/newspapers/refresh', methods=['GET'])
def preprocessing_newspaper_refresh():
    helper.collect_publisher_from_allmediaLink()
    return json.dumps({"msg":"ok"})


# =====================================================
# -------------------- HTTP CALL ----------------------
# =====================================================

@app.route('/preprocess/article', methods=['POST'])
def preprocessing_article():
    try:
        article = request.get_json(force=True)
        output=serv.execute_preprocess_article(article)
    except Exception as e:
        global_variables.logger.error(e)
        output = {'Error': 'Bad Request. Preprocessing ended with an error!'}
    return json.dumps(output)


# ======================================================================================================================
# ---------------------------------------------- STATIC SERVER --------------------------------------------------------
# ======================================================================================================================

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('www/', path)


if __name__ == '__main__':
    global_variables.init()
    #app.run(debug=False, host="192.168.0.22", port="5002")

    #-------------------------------------
    # ------------ DOCKER ----------------
    app.run(debug=False, host="0.0.0.0",port="5001")
    # -------------------------------------
