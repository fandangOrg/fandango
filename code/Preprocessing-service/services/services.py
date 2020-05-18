from helper import config as cfg
from helper import global_variables as gv
from helper.data_manager import DataManager
from helper.helper import generate_uuid_from_string, extract_domain_from_url
from helper.streaming_thread import StreamingThread


class PreprocessingServices:
    def __init__(self):
        self.service_name = cfg.service_name
        self.service_task = None
        self.data_manager = None

    def set_up_data_manager(self, service):
        try:
            self.data_manager = DataManager(service=service)
        except Exception as e:
            cfg.logger.error(e)

    def offline_service(self):
        error = False
        try:
            self.service_task = cfg.offline_service_name
            if gv.thread is None:
                # Set up data manager
                self.set_up_data_manager(service=self.service_task)

                # Init Kafka object
                self.data_manager.init_kafka_manager()

                # Check Kafka connector
                if not self.data_manager.kafka_manager.connection:
                    error = True
                kafka = self.data_manager.kafka_manager
                if kafka.consumer is not None:
                    gv.thread = StreamingThread(target=self.data_manager.start_kafka_process)
                    gv.thread.start()

            # Verify connection
            if error:
                output: dict = self.build_output(task_name=self.service_task, status=400,
                                                 message=cfg.aborted_msg)
            else:
                output: dict = self.build_output(task_name=self.service_task, status=200,
                                                 message=cfg.running_msg)
        except Exception as e:
            cfg.logger.error(e)
            output: dict = self.build_output(task_name=self.service_task, status=400,
                                             message=cfg.aborted_msg)
        return output

    def online_service(self, data):
        output: dict = {}
        try:
            self.service_task = cfg.online_service_name
            self.set_up_data_manager(service=self.service_task)

            # Pre-process data
            article_obj = self.data_manager.execute_preprocessing(data=data)

            # Generate output
            output: dict = article_obj.article_to_dict()
        except Exception as e:
            cfg.logger.error(e)
        return output

    def online_manual_service(self, data):
        try:
            self.service_task = cfg.manual_annotation_service_name
            self.set_up_data_manager(service=self.service_task)
            data["identifier"] = generate_uuid_from_string([data["title"], data["text"]])
            data["source_domain"] = extract_domain_from_url(data["url"])
            article_obj = self.data_manager.execute_preprocessing(data=data, manual_annot=True)
            # Generate output
            output = article_obj.article_to_dict()
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
        return output

    def experimental_offline_service(self):
        error = False
        try:
            self.service_task = cfg.experimental_service_name
            output: dict = self.build_output(task_name=self.service_task, status=200,
                                             message=cfg.running_msg)

            if gv.thread is None:
                # Set up data manager
                self.set_up_data_manager(service=self.service_task)

                # Init Kafka and Elasticsearch objects
                self.data_manager.init_kafka_manager()
                self.data_manager.init_elasticsearch_manager()

                if not self.data_manager.kafka_manager.connection:
                    error = True
                if not self.data_manager.elasticsearch_manager.connection:
                    error = True

                if not error:
                    # Check Elasticsearch index
                    self.data_manager.elasticsearch_manager.create_new_index(index=cfg.temp_es_index,
                                                                             body=None)
                    kafka = self.data_manager.kafka_manager

                    if kafka.consumer is not None:
                        gv.thread = StreamingThread(target=self.data_manager.start_experimental_kafka_process)
                        gv.thread.start()

                else:
                    output = self.build_output(task_name=self.service_task, status=400,
                                               message=cfg.aborted_msg)
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)

        return output

    def stop_service(self, service_name):
        try:
            self.service_task = service_name
            if gv.thread is not None and gv.thread.isAlive():
                gv.thread.kill()
                gv.thread.join()
                output = self.build_output(task_name=self.service_task, status=200,
                                           message=cfg.stop_msg)
            else:
                output = self.build_output(task_name=self.service_task, status=400,
                                           message=cfg.already_stop_msg)
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
            output['error'] = str(e)
        return output

    @staticmethod
    def build_output(task_name, status, message, data=None):
        output = {'service': task_name, 'status': status, 'message': message}
        try:
            if data is not None:
                output.update({'output': data})
        except Exception as e:
            cfg.logger.error(e)
        return output