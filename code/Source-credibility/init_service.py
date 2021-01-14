import json
import os
from flask import Flask, request, render_template
from flask_cors import CORS
from services.services import SourceCredibilityService
from helper.settings import (logger, host, port, static_folder,
                             templates_folder, swagger_template_file)
from fandango_models.source_credibility_models import GraphAnalyzerOutputDoc


app: Flask = Flask(__name__,
                   static_folder=static_folder,
                   template_folder=templates_folder)
CORS(app)


source_credibility_service: SourceCredibilityService = SourceCredibilityService()

# ======================================================================================================================
# ----------------------------------------------- GRAPH ANALYSIS SERVICES ----------------------------------------------
# ======================================================================================================================


@app.route('/api/graph_analysis/offline/start', methods=['POST'])
def graph_analysis_offline_service():
    output: GraphAnalyzerOutputDoc = source_credibility_service.offline_service()
    if output.status == 200:
        output: dict = output.__dict__
        return json.dumps(output)
    else:
        logger.error(f"\nStatus status: {output.status} \nMessage: {output.message}")
        # Kill the process
        os._exit(0)


@app.route('/api/graph_analysis/online/analyse_article', methods=['POST'])
def graph_analysis_online_service():
    data: dict = {}
    try:
        data: dict = request.json
    except Exception as e:
        pass
    output: GraphAnalyzerOutputDoc = source_credibility_service.online_service(
        data=data)
    output: dict = output.__dict__
    return json.dumps(output)


@app.route('/api/graph_analysis/author/<id>', methods=['GET'])
def get_author_object(id: str):
    output: GraphAnalyzerOutputDoc = source_credibility_service.get_author_object(
        id=id)
    response: dict = output.data
    return json.dumps(response)


@app.route('/api/graph_analysis/publisher/<id>', methods=['GET'])
def get_publisher_object(id: str):
    output: GraphAnalyzerOutputDoc = source_credibility_service.get_publisher_object(
        id=id)
    response: dict = output.data
    return json.dumps(response)


@app.route('/api/graph_analysis/docs')
def get_docs():
    return render_template(swagger_template_file)


if __name__ == '__main__':
    app.run(debug=False, host=host, port=port, threaded=True)
