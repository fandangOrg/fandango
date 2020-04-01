import json
import warnings
import os
from flask import Flask, request, render_template
from flask_cors import CORS
from services.services import GraphAnalysisService
from helper import global_variables as gv
from helper import config as cfg
from helper.helper import json_serial
from flask_swagger_ui import get_swaggerui_blueprint

warnings.filterwarnings('ignore')

app = Flask(__name__,
            static_folder=os.path.join(os.getcwd(), 'www'),
            template_folder=os.path.join(os.getcwd(), 'www'))
CORS(app)


serv = GraphAnalysisService()
# ======================================================================================================================
# ----------------------------------------------- GRAPH ANALYSIS SERVICES ----------------------------------------------
# ======================================================================================================================
@app.route('/search/<search_string>', methods=['GET'])
def search(search_string):
    return app.send_static_file('index.html')


@app.route('/', methods=['GET'])
def root():
    return app.send_static_file('index.html')

@app.route('/graph_analysis/offline/start', methods=['POST'])
def graph_analysis_offline_service():
    # -------------------------------------
    # ------------ DOCKER ----------------
    # os.system('./tunnel_kafka.sh')
    # --------------------------------------
    output = serv.offline_service()
    return json.dumps(output, default=json_serial)


@app.route('/graph_analysis/online/analyse_article', methods=['POST'])
def graph_analysis_online_service():
    data = request.get_json(force=True)
    output = serv.online_service(data=data)
    return json.dumps(output, default=json_serial)


@app.route('/graph_analysis/ui/domain_analysis', methods=['POST'])
def source_domain_analysis():
    # TODO: POST TO GET
    # 40.114.234.51:5000?publishername=elpais.com
    data = request.get_json(force=True)
    output = serv.source_domain_analysis(domain=data["domain"])
    return json.dumps(output, default=json_serial)

# ======================================================================================================================
# ======================================================================================================================

SWAGGER_URL = '/docs'
API_URL = '/www/swagger/swagger.json'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "FANDANGO Graph Service"})

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
# ======================================================================================================================

if __name__ == '__main__':
    gv.init()
    app.run(debug=False, host=cfg.host, port=cfg.port)

    #-------------------------------------
    # ------------ DOCKER ----------------
    #app.run(debug=False, host="0.0.0.0",port="5001")
    # -------------------------------------
