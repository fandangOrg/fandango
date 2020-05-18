import json, os
from flask import Flask, request
from flask_cors import CORS
from services.services import PreprocessingServices
from helper import global_variables as gv
from helper import config as cfg
from flask_swagger_ui import get_swaggerui_blueprint
import warnings
warnings.filterwarnings('ignore')

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


@app.route('/preprocessing/offline/start', methods=['POST'])
def preprocessing_offline_service():
    # -------------------------------------
    # ------------ DOCKER ----------------
    # os.system('./tunnel_kafka.sh')
    # --------------------------------------
    serv: PreprocessingServices = PreprocessingServices()
    output: dict = serv.offline_service()
    if output["status"] == 200:
        return json.dumps(output)
    else:
        # Kill the process
        os._exit(0)


@app.route('/preprocessing/offline/stop', methods=['POST'])
def stop_preprocessing_offline_service():
    serv: PreprocessingServices = PreprocessingServices()
    output: dict = serv.stop_service(service_name=cfg.offline_service_name)
    return json.dumps(output)


@app.route('/preprocessing/online/preprocess_article', methods=['POST'])
def preprocessing_online_service():
    serv: PreprocessingServices = PreprocessingServices()
    data = request.get_json(force=True)
    output: dict = serv.online_service(data=data)
    return json.dumps(output)


@app.route('/preprocessing/manual_annotation/preprocess_annotation', methods=['POST'])
def preprocessing_online_manual_service():
    serv: PreprocessingServices = PreprocessingServices()
    data = request.get_json(force=True)
    output = serv.online_manual_service(data=data)
    return json.dumps(output)


@app.route('/preprocessing/experimental_offline/start', methods=['POST'])
def start_experimental_offline_service():
    serv = PreprocessingServices()
    output: dict = serv.experimental_offline_service()
    if output["status"] == 200:
        return json.dumps(output)
    else:
        # Kill the process
        os._exit(0)


@app.route('/preprocessing/experimental_offline/stop', methods=['POST'])
def stop_experimental_offline_service():
    serv = PreprocessingServices()
    output = serv.stop_service(service_name=cfg.experimental_service_name)
    return json.dumps(output)

# ==================================================================
# ==================================================================
# ==================================================================


if __name__ == '__main__':
    gv.init()
    app.run(debug=False, host=cfg.host, port=cfg.port, threaded=True)

