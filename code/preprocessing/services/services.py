from helper import global_variables as gv
from helper.data_manager import DataManager
from helper.helper import generate_uuid_from_string, extract_domain_from_url
from helper.thread_utils import kill_streaming_thread, start_offline_process
from models.preprocessing_models import PreprocessingOutputDocument
from typing import Optional


class PreprocessingServices:
    def __init__(self):
        self.service_name: str = gv.service_name
        self.service_task: str = ""
        self.data_manager: Optional[DataManager] = None

    def set_up_data_manager(self, service):
        try:
            self.data_manager: DataManager = DataManager(service=service)
        except Exception as e:
            gv.logger.error(e)

    def verify_external_server_connections(self, kafka: bool = True, es: bool = True):
        connection_error: dict = {"Kafka": False, "ES": False}
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

        except Exception as e:
            gv.logger.error(e)
        return connection_error

    def offline_service(self):
        output: PreprocessingOutputDocument = self.build_output_object(message=gv.http_response_500,
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
            output: PreprocessingOutputDocument = self.build_output_object(message=message,
                                                                           status=status)

        except Exception as e:
            gv.logger.error(e)
        return output

    def online_service(self, data: dict):
        output: PreprocessingOutputDocument = self.build_output_object(message=gv.http_response_500,
                                                                       status=500)
        try:
            if "data" in data.keys():
                input_data: dict = data["data"]
            else:
                input_data: dict = data

            self.service_task = gv.online_service_name
            self.set_up_data_manager(service=self.service_task)
            output: PreprocessingOutputDocument = self.data_manager.execute_preprocessing(data=input_data)

        except Exception as e:
            gv.logger.error(e)
        return output

    def online_manual_service(self, data: dict):
        output: PreprocessingOutputDocument = self.build_output_object(message=gv.http_response_500,
                                                                       status=500)
        try:
            self.service_task = gv.manual_annotation_service_name
            self.set_up_data_manager(service=self.service_task)
            data["identifier"] = generate_uuid_from_string([data["title"], data["text"]])
            data["source_domain"] = extract_domain_from_url(data["url"])

            output: PreprocessingOutputDocument = self.data_manager.execute_preprocessing(
                data=data, manual_annot=True)

        except Exception as e:
            gv.logger.error(e)
        return output

    def experimental_offline_service(self):
        output: PreprocessingOutputDocument = self.build_output_object(message=gv.http_response_500,
                                                                       status=500)
        try:
            self.service_task = gv.experimental_service_name

            # 1. Set up data manager
            self.set_up_data_manager(service=self.service_task)

            # 2. Verify Connection
            connection_error: dict = self.verify_external_server_connections()

            # 3. If there is an error in any external connection
            if True in list(connection_error.values()):
                status: int = 403
                message: str = gv.http_response_403
            else:
                # 3.1 Check Elasticsearch temporal index
                self.data_manager.elasticsearch_manager.create_new_index(index=gv.temp_es_index,
                                                                         body=None)

                # 3.2 Start offline process
                response: dict = start_offline_process(
                    thread_name=self.service_task,
                    target_func=self.data_manager.start_experimental_kafka_process)

                status: int = response["status"]
                message: str = response["message"]

            # 4. Build output
            output: PreprocessingOutputDocument = self.build_output_object(message=message, status=status)

        except Exception as e:
            gv.logger.error(e)
        return output

    def stop_service(self, service_name):
        output: PreprocessingOutputDocument = self.build_output_object(
            message=gv.http_response_500,
            status=500)
        try:
            self.service_task = service_name
            # find thread by name
            # If the list of threads is not empty
            if gv.offline_threads:
                # Check if there is a thread with the same name running
                thread_names = [i.name for i in gv.offline_threads]
                # Thread with the same name
                if service_name in thread_names:
                    thread_idx = thread_names.index(service_name)
                    # Stop selected thread
                    current_thread = gv.service_name[thread_idx]
                    response = kill_streaming_thread(streaming_thread=current_thread)
                    if response:
                        status: int = 200
                        message: str = gv.http_response_200
                    else:
                        status: int = 422
                        message: str = gv.http_response_422
                    output: PreprocessingOutputDocument = self.build_output_object(message=message,
                                                                                   status=status)
        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def build_output(task_name: str, status: int, message: str, data: dict = None):
        output = {'service': task_name, 'status': status, 'message': message}
        try:
            if data is not None:
                output.update({'output': data})
        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def build_output_object(message: str, status: int, data: dict = None):
        output: PreprocessingOutputDocument = PreprocessingOutputDocument(message=message,
                                                                          status=status,
                                                                          data=data)
        return output
