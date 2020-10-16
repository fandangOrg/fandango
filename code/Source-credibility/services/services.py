from helper import global_variables as gv
from managers.data_manager import DataManager
from typing import Optional
from helper.thread_utils import start_offline_process
from models.graph_models import GraphAnalyzerOutputDoc, AnalysisDoc


class GraphAnalysisService:
    def __init__(self):
        self.service_name: str = gv.service_name
        self.service_task: str = ""
        self.data_manager: Optional[DataManager] = None

    def set_up_data_manager(self, service):
        try:
            self.data_manager: DataManager = DataManager(service=service)
        except Exception as e:
            gv.logger.error(e)
        return self

    def verify_external_server_connections(self, kafka: bool = True, es: bool = True,
                                           neo4j: bool = True):
        connection_error: dict = {"Kafka": False, "ES": False, "NEO4J": False}
        try:
            if kafka:
                # ------------ Kafka -----------------------------
                # Init Kafka object
                if self.data_manager.kafka_manager is None:
                    self.data_manager.verify_kafka_connection()

                # Verify Kafka Connection
                if not self.data_manager.kafka_manager.connection:
                    connection_error["Kafka"] = True
            if es:
                # ------------- ES ---------------------------------
                # Init Elasticsearch object
                if self.data_manager.elasticsearch_manager is None:
                    self.data_manager.init_elasticsearch_manager()

                # Verify ES Connection
                if not self.data_manager.elasticsearch_manager.connection:
                    connection_error["ES"] = True
            if neo4j:
                # ------------- Neo4j ---------------------------------
                # Init Neo4j object
                if self.data_manager.neo4j_manager is None:
                    self.data_manager.init_neo4j_manager()

                # Verify NEO4J Connection
                if not self.data_manager.neo4j_manager.connection:
                    connection_error["NEO4J"] = True

        except Exception as e:
            gv.logger.error(e)
        return connection_error

    def offline_service(self):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(message=gv.http_response_500,
                                                                status=500)
        try:
            self.service_task: str = gv.offline_service_name

            # 1. Set up data manager
            self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections()

            # 3. If there is an error in any external connection
            if True in list(connection_error.values()):
                status: int = 403
                message: str = gv.http_response_403
            else:
                # 4. Start offline process
                response: dict = start_offline_process(
                    thread_name=self.service_task,
                    target_func=self.data_manager.start_kafka_offline_process)

                status: int = response["status"]
                message: str = response["message"]

            # 4. Build output
            output.message: str = message
            output.status: int = status

        except Exception as e:
            gv.logger.error(e)
        return output

    def online_service(self, data):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=gv.http_response_500,
            status=500, data=AnalysisDoc().dict_from_class())
        try:
            output_data: dict = {"authorRating": [], "publisherRating": []}

            # 1. Initialise Data Manager
            self.service_task = gv.online_service_name
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(kafka=False)

            # 3. Start process
            if True in list(connection_error.values()):
                status: int = 403
                message: str = gv.http_response_403
                output_data.update(output.data)
            else:
                # 3.1 Execute Graph Analysis
                response: GraphAnalyzerOutputDoc = self.data_manager.execute_graph_analysis(
                    document=data)
                output_data.update(response.data)

                # 3.2 Check response
                if response.status == 200:
                    # 3.2.1 Add author rating
                    output_data["authorRating"]: list = self.data_manager.get_ratings_from_identifiers(
                        index=gv.person_es_index,
                        identifiers=response.data["authors"],
                        key=gv.score_name)

                    # 3.2.2 Add publisher ratings
                    output_data["publisherRating"] = self.data_manager.get_ratings_from_identifiers(
                        index=gv.org_es_index, identifiers=response.data["publisher"], key=gv.score_name)

                # 5. Add data to response
                message: str = response.message
                status: int = response.status

            output.message: str = message
            output.status: int = status
            output.data: dict = output_data

        except Exception as e:
            gv.logger.error(e)
        return output

    def source_domain_analysis(self, domain):
        try:
            self.service_task = gv.online_service_name
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # Execute Graph Analysis
            output = self.data_manager.execute_source_domain_analysis(full_domain=domain)
        except Exception as e:
            gv.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=gv.aborted_msg)
        return output

    def get_author_object(self, id: str):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=gv.http_response_500,
            status=500, data={})
        try:
            # 1. Initialise Data Manager
            self.service_task = "get_authors"
            data: dict = {}
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(
                kafka=False, neo4j=False)

            # 3. Start process
            if True in list(connection_error.values()):
                status: int = 403
                message: str = gv.http_response_403

            else:
                data: dict = self.data_manager.get_object_from_elasticsearch(
                    index=gv.person_es_index, identifier=id)
                status: int = 200
                message: str = gv.http_response_200

            # 4. Build response
            output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=message,
                status=status, data=data)

        except Exception as e:
            gv.logger.error(e)
        return output

    def get_publisher_object(self, id: str):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=gv.http_response_500,
            status=500, data={})
        try:
            # 1. Initialise Data Manager
            self.service_task = "get_publisher"
            data: dict = {}
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(
                kafka=False, neo4j=False)

            # 3. Start process
            if True in list(connection_error.values()):
                status: int = 403
                message: str = gv.http_response_403
            else:
                data: dict = self.data_manager.get_object_from_elasticsearch(
                    index=gv.org_es_index, identifier=id)
                status: int = 200
                message: str = gv.http_response_200

            # 4. Build response
            output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=message,
                status=status, data=data)

        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def build_output(task_name, status, message, data=None):
        output = {'service': task_name, 'status': status, 'message': message}
        try:
            if data is not None:
                output.update({'output': data})
        except Exception as e:
            gv.logger.error(e)
        return output