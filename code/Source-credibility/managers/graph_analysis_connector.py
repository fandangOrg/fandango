import datetime
import os, requests
from models.article import Article
from models.author import Author
from models.publisher import Publisher
from models.graph_models import GraphAnalyzerOutputDoc, AnalysisDoc, Neo4jInputDoc, SourceCredibilityOutputDoc
from helper.helper import extract_domain_from_url
from helper import global_variables as gv
from helper.thread_utils import start_offline_process
from graph_analysis.source_credibility_analysis import SourceCredibility
from managers.neo4j_connector import NEO4JConnector
from managers.elasticsearch_connector import ElasticsearchManager


class GraphAnalysis:
    def __init__(self, neo4j_connector: NEO4JConnector,
                 elasticsearch_connector: ElasticsearchManager):

        self.neo4j_connector: NEO4JConnector = neo4j_connector
        self.elasticsearch_connector: ElasticsearchManager = elasticsearch_connector
        self.source_credibility_analyzer: SourceCredibility = SourceCredibility(
            es_connector=elasticsearch_connector,
            neo4j_connector=neo4j_connector)
        self.person_index: str = gv.person_es_index
        self.publisher_index: str = gv.org_es_index
        self.csv_filepath: str = os.path.join(gv.resources_dir, gv.csv_filepath)
        self.countries_website: list = gv.countries_websites

    def extract_authors_from_document(self, document: Article):
        author_data = {"identifier": [], "source_data": []}
        try:
            domain_info = extract_domain_from_url(document.url)
            source_domain = domain_info.domain
            for aut_name in document.authors:

                # Considering Name + source_domain
                uuid_aut = self.elasticsearch_connector.generate_uuid_from_string(data_uuid=[aut_name,
                                                                                             source_domain])

                # Check if the author is already in Elasticsearch by uuid
                response = self.elasticsearch_connector.retrieve_data_from_index_by_id(index=self.person_index,
                                                                                       uuid=uuid_aut)
                source_data = response
                # If it does not exist yet
                if not response:
                    author_obj = Author(identifier=uuid_aut, name=aut_name, affiliation=document.publisher,
                                        url=document.url)
                    source_data = author_obj.to_source_data_dict()
                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(index=self.person_index,
                                                                                 uuid=uuid_aut,
                                                                                 source_data=source_data)
                # Append data to response
                author_data["identifier"].append(uuid_aut)
                author_data["source_data"].append(source_data)
        except Exception as e:
            gv.logger.error(e)
        return author_data

    def extract_publisher_from_document(self, document):
        publisher_data = {"identifier": [], "source_data": []}
        try:
            if not isinstance(document.publisher, list):
                document.publisher = [document.publisher]

            for pub_name in document.publisher:
                domain_info = extract_domain_from_url(document.url)
                url = domain_info.domain
                data_uuid = [url]

                # Check if the publisher is already in Elasticsearch by uuid
                uuid_pub = self.elasticsearch_connector.generate_uuid_from_string(data_uuid=data_uuid)
                response = self.elasticsearch_connector.retrieve_data_from_index_by_id(index=self.publisher_index,
                                                                                       uuid=uuid_pub)
                source_data = response
                # If it does not exist yet
                if not response:
                    pub_obj = Publisher(identifier=uuid_pub, name=pub_name, url=document.sourceDomain,
                                        country=document.country, nationality=document.nationality)

                    source_data = pub_obj.to_source_data_dict()

                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(index=self.publisher_index,
                                                                                 uuid=uuid_pub,
                                                                                 source_data=source_data)
                # Append data to response
                publisher_data["identifier"].append(uuid_pub)
                publisher_data["source_data"].append(source_data)
        except Exception as e:
            gv.logger.error(e)
        return publisher_data

    def apply_graph_analysis(self, document: Article):
        response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=gv.http_response_500,
            status=500,
            data=AnalysisDoc().dict_from_class())
        try:
            # 1. Extract Authors from document
            authors_data: dict = self.extract_authors_from_document(document=document)

            # 2. Extract Publisher
            publisher_data: dict = self.extract_publisher_from_document(document=document)

            # 3. Merge data into Neo4j input doc
            document_neo4j: Neo4jInputDoc = Neo4jInputDoc(
                article=document.article_to_dict(),
                authors=authors_data, publisher=publisher_data)

            # 4. Add to queue
            self.add_document_to_queue(document=document_neo4j)

            # 5. Generate analysis response
            output_analysis: AnalysisDoc = self.build_graph_response(
                identifier=document.identifier,
                authors_data=authors_data,
                publisher_data=publisher_data)

            # 6. check status of the NE4OJ thread
            response_threads: dict = start_offline_process(
                thread_name=gv.neo4j_thread_name,
                target_func=self.analyse_data_from_neo4j_queue)

            # 7. Generate service response
            response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=response_threads["message"],
                status=response_threads["status"],
                data=output_analysis.dict_from_class())

        except Exception as e:
            gv.logger.error(e)
        return response

    @staticmethod
    def add_document_to_queue(document: Neo4jInputDoc):
        try:
            gv.queue_neo4j.put(document)
            gv.event.set()
        except Exception as e:
            gv.logger.error(e)

    def analyse_data_from_neo4j_queue(self):
        try:
            while not gv.queue_neo4j.empty():

                # 1. Load input document to be analysed
                neo4j_data: Neo4jInputDoc = gv.queue_neo4j.get()

                # 2. Start graph process
                response: SourceCredibilityOutputDoc = self.source_credibility_analyzer.start_analysis(
                    document=neo4j_data)

                # 3. Update scores and status into Elasticsearch
                self.update_analysis_into_elasticsearch(
                    data_to_update=response.data,
                    keys=list(response.data.keys()))

                gv.logger.info("Document " + neo4j_data.article["identifier"] +
                               " was added and analyzed correctly in NEO4J Graph" +
                               " at " + (datetime.datetime.now().strftime("%c")) + "\n")
                
                # 4. POST Fusion Score
                gv.logger.info("Calling Fusion Score Service")
                response_fusion_score: dict = self.update_fusion_score(
                    server=gv.fusion_score_server,
                    port=gv.fusion_score_port,
                    endpoint=gv.fusion_score_endpoint,
                    article_uuid=neo4j_data.article["identifier"])

                if response_fusion_score["status"] == 200:
                    gv.logger.info("Fusion score updated with success!")

                # 5. Clear Element of Queue
                gv.event.clear()

                # 6. End process
                if gv.queue_neo4j.empty():
                    gv.event.wait()
                    gv.event.clear()
            gv.logger.warning('No more data to be analysed!')
        except Exception as e:
            gv.logger.error(e)

    @staticmethod
    def update_fusion_score(server: str, port: str, endpoint: str, article_uuid: str):
        response: dict = {"status": 500, "message": gv.http_response_500}
        try:
            url: str = f"http://{server}:{port}/{endpoint}"
            data: dict = {"identifier": article_uuid}
            response_api = requests.post(url=url, json=data, timeout=3)
            response["status"]: int = response_api.status_code
            if response_api.status_code == 200:
                response["message"]: str = gv.http_response_200
        except Exception as e:
            gv.logger.error(e)
        return response

    @staticmethod
    def build_graph_response(identifier: str, authors_data: dict, publisher_data: dict):
        response: AnalysisDoc = AnalysisDoc()
        try:
            authors_uuids: list = authors_data["identifier"]
            publisher_uuids: list = publisher_data["identifier"]
            response: AnalysisDoc = AnalysisDoc(identifier=identifier, authors=authors_uuids,
                                                publisher=publisher_uuids)
        except Exception as e:
            gv.logger.error(e)
        return response

    def update_analysis_into_elasticsearch(self, data_to_update: dict, keys: list):
        try:
            for k in keys:
                n_elements: int = len(data_to_update[k]["uuids"])
                for i in range(n_elements):
                    uuid: str = data_to_update[k]["uuids"][i]
                    trustworthiness: float = data_to_update[k]["scores"][i]
                    status: int = data_to_update[k]["status"][i]
                    index: str = data_to_update[k]["index"][i]

                    params = {"trustworthiness": trustworthiness, "status": status}
                    body = {"doc": params}
                    self.elasticsearch_connector.update_fields_to_index(index=index, uuid=uuid,
                                                                        body=body)
        except Exception as e:
            gv.logger.error(e)

    def analyse_publisher_ui(self, full_domain):
        response: dict = {}
        try:
            response = self.source_credibility_analyzer.retrieve_source_information(
                graph=self.neo4j_connector.graph,
                full_domain=full_domain,
                es_connector=self.elasticsearch_connector,
                es_index=self.publisher_index)
        except Exception as e:
            gv.logger.error(e)
        return response