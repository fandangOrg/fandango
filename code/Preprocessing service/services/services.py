from helper import config as cfg
from helper import global_variables as gv
from helper.data_manager import DataManager
from helper.helper import generate_uuid_article, extract_domain_from_url
from threading import Thread


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
        return self

    def offline_service(self):
        try:
            self.service_task = cfg.offline_service_name
            if gv.thread is None:
                # Set up data manager
                self.set_up_data_manager(service=self.service_task)
                # Init Kafka object
                self.data_manager.init_kafka_manager()
                kafka = self.data_manager.kafka_manager
                if (kafka.consumer is not None):
                    gv.thread = Thread(target=self.data_manager.start_kafka_process)
                    gv.thread.start()

            output = self.build_output(task_name=self.service_task, status=200,
                                       message=cfg.running_msg)
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
            output['error'] = str(e)
        return output

    def online_service(self, data):
        try:
            self.service_task = cfg.online_service_name
            self.set_up_data_manager(service=self.service_task)

            # Pre-process data
            article_obj = self.data_manager.execute_preprocessing(data=data)

            # Generate output
            output = article_obj.article_to_dict()
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
        return output

    def online_manual_service(self, data):
        try:
            self.service_task = cfg.manual_annotation_service_name
            self.set_up_data_manager(service=self.service_task)
            # TODO: Check identifier of the data in case to need to compute it
            data["identifier"] = generate_uuid_article(data["url"])
            data["source_domain"] = extract_domain_from_url(data["url"])
            article_obj = self.data_manager.execute_preprocessing(data=data, manual_annot=True)

            # Generate output
            output = article_obj.article_to_dict()
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
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