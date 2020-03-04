'''
Created on Jan 21, 2019

@author: daniele
'''
import datetime
import threading
from brokermanager.model.publishers import KafkaPublisher
from fake_news_detection.config.AppConfig import url_kafka, port_kafka, group_id
from fake_news_detection.apps.KafkaCons import InjectableTASKJSONConsumer
from fake_news_detection.apps.Task import Task


class Job_consumer(threading.Thread):

    def __init__(self, threadID, topic_input, topic_output, task, **args):
        threading.Thread.__init__(self)
        self.threadID = threadID
        #===========================================================================
        #         consumer=InjectableTASKJSONConsumer(topic = topic, group_id="lvt_group2", bootstrap_servers=["localhost:9092"], task=Task_1(queue_output,output_topic))
        # print('          3            ')
        # consumer.consume_forever()
        # print('                4           ')
        # print("in ascolto")
        #===========================================================================
        queue_output = KafkaPublisher(url_kafka, port_kafka)  # provo se la coda è stata creata
        bootstrap_servers = [url_kafka + ":" + port_kafka]
        task = task(queue_output, topic_output)
        self.consumer = InjectableTASKJSONConsumer(topic=topic_input, group_id=group_id, bootstrap_servers=bootstrap_servers, task=task)
        self.args = args
        
    def run(self):
            self.consumer.consume_forever()


def run_job(input_queue, task:Task, output_queue=None, n_job=10, **args):
    print("N_JOB ", n_job)
    for n in range(int(n_job)):
        thread1 = Job_consumer("Thread-Scodatore-" + str(n), input_queue , output_queue, task, **args)
        thread1.start()
    print("======================")

