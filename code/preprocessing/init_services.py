import json, os
from flask import Flask, request
from flask_cors import CORS
from services.services import PreprocessingServices
from helper import global_variables as gv
from models.preprocessing_models import PreprocessingOutputDocument
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "FANDANGO Preprocessing Service"})

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# ======================================================================================================================
# ----------------------------------------------- PRE-PROCESSING SERVICES ----------------------------------------------
# ======================================================================================================================


@app.route('/api/preprocessing/offline/start', methods=['POST'])
def preprocessing_offline_service():
    serv: PreprocessingServices = PreprocessingServices()
    output: PreprocessingOutputDocument = serv.offline_service()
    if output.status == 200:
        output: dict = output.dict_from_class()
        return json.dumps(output)
    else:
        gv.logger.error("\nStatus status: %s \nMessage: %s ", output.status, output.message)
        # Kill the process
        os._exit(0)


@app.route('/api/preprocessing/offline/stop', methods=['POST'])
def stop_preprocessing_offline_service():
    serv: PreprocessingServices = PreprocessingServices()
    output: PreprocessingOutputDocument = serv.stop_service(service_name=gv.offline_service_name)
    if output.status == 200 or output.status == 400:
        output: dict = output.dict_from_class()
        return json.dumps(output)
    elif output.status == 500:
        gv.logger.error("\nStatus status: %s \nMessage: %s ", output)
        # Kill the process
        os._exit(0)


@app.route('/api/preprocessing/online/preprocess_article', methods=['POST'])
def preprocessing_online_service():
    data = request.get_json(force=True)
    serv: PreprocessingServices = PreprocessingServices()
    output: PreprocessingOutputDocument = serv.online_service(data=data)
    output: dict = output.dict_from_class()
    return json.dumps(output)


@app.route('/api/preprocessing/manual_annotation/preprocess_annotation', methods=['POST'])
def preprocessing_online_manual_service():
    serv: PreprocessingServices = PreprocessingServices()
    data = request.get_json(force=True)
    output: PreprocessingOutputDocument = serv.online_manual_service(data=data)
    output: dict = output.dict_from_class()
    return json.dumps(output)


@app.route('/api/preprocessing/experimental_offline/start', methods=['POST'])
def start_experimental_offline_service():
    serv: PreprocessingServices = PreprocessingServices()
    output: PreprocessingOutputDocument = serv.experimental_offline_service()

    if output.status == 200:
        output: dict = output.dict_from_class()
        return json.dumps(output)
    else:
        gv.logger.error("\nStatus status: %s \nMessage: %s ", output)
        # Kill the process
        os._exit(0)


@app.route('/api/preprocessing/experimental_offline/stop', methods=['POST'])
def stop_experimental_offline_service():
    serv: PreprocessingServices = PreprocessingServices()
    output: PreprocessingOutputDocument = serv.stop_service(
        service_name=gv.experimental_service_name)
    if output.status == 200 or output.status == 400:
        output: dict = output.dict_from_class()
        return json.dumps(output)
    elif output.status == 500:
        gv.logger.error("\nStatus status: %s \nMessage: %s ", output)
        # Kill the process
        os._exit(0)

# ==================================================================
# ==================================================================
# ==================================================================


if __name__ == '__main__':
    gv.init_threads()
    gv.download_ner_models_background()
    app.run(debug=False, host=gv.host, port=gv.port, threaded=True)

