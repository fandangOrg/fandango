import json
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
    serv = PreprocessingServices()
    output = serv.offline_service()
    return json.dumps(output)


@app.route('/preprocessing/online/preprocess_article', methods=['POST'])
def preprocessing_online_service():
    serv = PreprocessingServices()
    data = request.get_json(force=True)
    output = serv.online_service(data=data)
    return json.dumps(output)

@app.route('/preprocessing/manual_annotation/preprocess_annotation', methods=['POST'])
def preprocessing_online_manual_service():
    serv = PreprocessingServices()
    data = request.get_json(force=True)
    output = serv.online_manual_service(data=data)
    return json.dumps(output)


if __name__ == '__main__':
    gv.init()
    app.run(debug=False, host=cfg.host, port=cfg.port)

    #-------------------------------------
    # ------------ DOCKER ----------------
    #app.run(debug=False, host="0.0.0.0",port="5001")
    # -------------------------------------
