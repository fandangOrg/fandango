from helper import config as cfg
from helper import global_variables as gv
from helper.data_manager import DataManager
from threading import Thread


class GraphAnalysisService:
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
                if self.data_manager is None:
                    self.set_up_data_manager(service=self.service_task)
                    # Init Kafka object
                if self.data_manager.kafka_manager is None:
                    self.data_manager.init_kafka_manager()
                kafka = self.data_manager.kafka_manager
                if kafka.consumer is not None:
                    gv.thread = Thread(target=self.data_manager.start_offline_process)
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
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # Execute Graph Analysis
            output = self.data_manager.execute_graph_analysis(document=data)

            # Add author rating
            output["authorRating"] = self.data_manager.get_ratings_from_identifiers(index=cfg.person_es_index,
                                                                                    identifiers=output["authors"],
                                                                                    key=cfg.score_name)
            # Add publisher ratings
            output["publisherRating"] = self.data_manager.get_ratings_from_identifiers(index=cfg.org_es_index,
                                                                                       identifiers=output["publisher"],
                                                                                       key=cfg.score_name)
        except Exception as e:
            cfg.logger.error(e)
            output = self.build_output(task_name=self.service_task, status=400,
                                       message=cfg.aborted_msg)
        return output

    def source_domain_analysis(self, domain):
        try:
            self.service_task = cfg.online_service_name
            if self.data_manager is None:
                self.set_up_data_manager(service=self.service_task)

            # Execute Graph Analysis
            output = self.data_manager.execute_source_domain_analysis(full_domain=domain)
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