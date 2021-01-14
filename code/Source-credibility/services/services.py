from helper.settings import (logger, service_name, http_response_200,
                             http_response_403,
                             http_response_409,
                             http_response_500,
                             online_service_name,
                             offline_service_name,
                             org_es_index, person_es_index, score_key)
from connectors.data_connector import DataConnector
from typing import Optional
from helper.streaming_thread import ThreadsProcessor
from fandango_models.source_credibility_models import GraphAnalyzerOutputDoc, AnalysisDoc, GeneralAPIResponse


class SourceCredibilityService:
    def __init__(self):
        self.service_name: str = service_name
        self.service_task: str = ""
        self.data_connector: Optional[DataConnector] = None

    def set_up_data_manager(self, service):
        try:
            self.data_connector: DataConnector = DataConnector(
                service=service)
        except Exception as e:
            logger.error(e)
        return self

    def verify_external_server_connections(self, kafka: bool = True, es: bool = True):
        connection_error: dict = {"Kafka": False, "ES": False}
        try:
            if kafka:
                # ------------ Kafka -----------------------------
                # Init Kafka object
                if self.data_connector.kafka_manager is None:
                    self.data_connector.verify_kafka_connection()

                # Verify Kafka Connection
                if not self.data_connector.kafka_manager.connection:
                    connection_error["Kafka"] = True
            if es:
                # ------------- ES ---------------------------------
                # Init Elasticsearch object
                if self.data_connector.elasticsearch_connector.es is None:
                    self.data_connector.init_elasticsearch_connector()

                # Verify ES Connection
                if not self.data_connector.elasticsearch_connector.connection:
                    connection_error["ES"] = True

        except Exception as e:
            logger.error(e)
        return connection_error

    def offline_service(self):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(message=http_response_500,
                                                                status=500)
        try:
            self.service_task: str = offline_service_name
            if self.data_connector is None:
                # 1. Set up data manager
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections()

            # 3. If there is an error in any external connection
            if True in list(connection_error.values()):
                status: int = 403
                message: str = http_response_403
            else:
                # 4. Start offline process
                response: GeneralAPIResponse = ThreadsProcessor.start_new_streaming_process(
                    thread_name=self.service_task,
                    target_func=self.data_connector.start_kafka_offline_process)

                status: int = response.status_code
                message: str = response.message

            # 5. Build output
            output.message: str = message
            output.status: int = status

        except Exception as e:
            logger.error(e)
        return output

    def online_service(self, data):
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=http_response_500,
            status=500, data=AnalysisDoc().__dict__)
        try:
            output_data: dict = {"authorRating": [], "publisherRating": []}

            # 1. Initialise Data Manager
            self.service_task = online_service_name
            if self.data_connector is None:
                self.set_up_data_manager(
                    service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(kafka=False)

            # 3. Start process ONLY IF Elasticsearch is available
            if True in list(connection_error.values()):
                status: int = 409
                message: str = http_response_409
                output_data.update(output.data)
            else:
                # 3.1 Execute Graph Analysis
                response: GraphAnalyzerOutputDoc = self.data_connector.process_source_credibility_analysis(
                    document=data)
                output_data.update(response.data)

                # 3.2 Check response
                if response.status == 200:
                    # 3.2.1 Add author rating
                    output_data["authorRating"]: list = self.data_connector.get_ratings_from_identifiers(
                        index=person_es_index,
                        identifiers=response.data["authors"],
                        key=score_key)

                    # 3.2.2 Add publisher ratings
                    output_data["publisherRating"] = self.data_connector.get_ratings_from_identifiers(
                        index=org_es_index, identifiers=response.data["publisher"], key=score_key)

                # 5. Add data to response
                message: str = response.message
                status: int = response.status

            output.message: str = message
            output.status: int = status
            output.data: dict = output_data

        except Exception as e:
            logger.error(e)
        return output

    def get_author_object(self, id: str) -> GraphAnalyzerOutputDoc:
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=http_response_500,
            status=500, data={})
        try:
            # 1. Initialise Data Manager
            self.service_task = "get_authors"
            data: dict = {}

            if self.data_connector is None:
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(
                kafka=False)

            # 3. Start process
            if True in list(connection_error.values()):
                status: int = 403
                message: str = http_response_403

            else:
                data: dict = self.data_connector.get_object_from_elasticsearch(
                    index=person_es_index, identifier=id)
                status: int = 200
                message: str = http_response_200

            # 4. Build response
            output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=message,
                status=status,
                data=data)

        except Exception as e:
            logger.error(e)
        return output

    def get_publisher_object(self, id: str) -> GraphAnalyzerOutputDoc:
        output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=http_response_500,
            status=500, data={})
        try:
            # 1. Initialise Data Manager
            self.service_task = "get_publisher"
            data: dict = {}

            if self.data_connector is None:
                self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections(
                kafka=False)

            # 3. Start process
            if True in list(connection_error.values()):
                status: int = 403
                message: str = http_response_403
            else:
                data: dict = self.data_connector.get_object_from_elasticsearch(
                    index=org_es_index, identifier=id)
                status: int = 200
                message: str = http_response_200

            # 4. Build response
            output: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=message,
                status=status,
                data=data)

        except Exception as e:
            logger.error(e)
        return output

    @staticmethod
    def build_output(task_name, status, message, data=None) -> dict:
        output: dict = {'service': task_name, 'status': status, 'message': message}
        try:
            if data is not None:
                output.update({'output': data})
        except Exception as e:
            logger.error(e)
        return output