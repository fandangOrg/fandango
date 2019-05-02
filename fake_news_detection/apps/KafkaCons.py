'''
Created on 7 mar 2019

@author: camila
'''

from kafka.consumer.group import KafkaConsumer 
import logging
import time
import json
import random
import os
#from fake_news_detection.apps.consumers import Task, Task_1
from brokermanager.model.publishers import KafkaPublisher
from fake_news_detection.apps.Task import Task,Task_1


class Consumer:
    def __init__(self,topic,group_id,bootstrap_servers,auto_offset_reset="earliest",enable_auto_commit=False,retry_interval=1):
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.retry_interval = retry_interval
        self.topic = topic

    def consume_forever(self):
        consumer=None
        while True:
            try:
                consumer=KafkaConsumer(self.topic,group_id=self.group_id,bootstrap_servers=self.bootstrap_servers,auto_offset_reset=self.auto_offset_reset,enable_auto_commit=self.enable_auto_commit)
                consumer.poll()
                for msg in consumer:
                    try:
                        obj=self.parse(msg)
                        self.process(obj)
                        consumer.commit()
                    except Exception as elab:
                        logging.exception(elab)
            except Exception as inst:
                logging.exception(inst)
                time.sleep(self.retry_interval)
            finally:
                if consumer:
                    try:
                        consumer.close()
                    except Exception as cl:
                        logging.exception(cl)

    def parse(self,msg):
        raise Exception("Not implemented")
    
    def process(self,obj):
        raise Exception("Not implemented")
    
    

class JsonConsumer(Consumer):
    def parse(self, msg):
        try:
            return json.loads(msg.value)
        except Exception as inst:
            print(inst)
            return None
    
    #take just one function at time
class InjectableJSONConsumer(JsonConsumer):
    def __init__(self,topic,group_id,bootstrap_servers,fun,auto_offset_reset="earliest",enable_auto_commit=True,retry_interval=1):
        super().__init__(topic,group_id, bootstrap_servers, auto_offset_reset, enable_auto_commit, retry_interval)
        self.fun=fun
    def process(self, obj):
        return self.fun(obj)
    
    #take some tasks together
class InjectableTASKJSONConsumer(JsonConsumer):  
    def __init__(self,topic,group_id,bootstrap_servers,task:Task,auto_offset_reset="earliest",enable_auto_commit=True,retry_interval=1):
        super().__init__(topic,group_id, bootstrap_servers, auto_offset_reset, enable_auto_commit, retry_interval)
        self.task=task
        
       
    def process(self, obj):
        print(self.task.do(obj))
        return self.task.do(obj)
    
    

    def init_system(self):
    #load (carica modelli)    
    #{"it":modello,"en":modello}
        pass
      
      



if __name__ == '__main__':
    '''
    def print_f(obj):
        print("new record", obj)
    
    consumer=InjectableJSONConsumer(topic="input_preprocessed", group_id="cami2", bootstrap_servers=["localhost:9092"], fun=print_f)
    consumer.consume_forever()
    
        
   
    queue_output=KafkaPublisher("localhost","9092")#provo se la coda è stata creata
    consumer=InjectableJSONConsumer(topic="input_preprocessed", group_id="cami2", bootstrap_servers=["localhost:9092"], fun=print_f)
    consumer.consume_forever()
 
    '''
    
    
    
          
    #consumer=InjectableJSONConsumer(topic="score_ml", group_id="cami2", bootstrap_servers=["localhost:9092"], fun=print_f)
    #consumer.consume_forever()
    #print("errore")
    
    
    print('  1      ')
    queue_output=KafkaPublisher("localhost","9092")#provo se la coda è stata creata
    topic="input_preprocessed"
    output_topic =  "analyzed_text"
    print('     2                ')
    consumer=InjectableTASKJSONConsumer(topic = topic, group_id="lvt_group2", bootstrap_servers=["localhost:9092"], task=Task_1(queue_output,output_topic))
    print('          3            ')
    consumer.consume_forever()
    print('                4           ')
    print("in ascolto")

    
    
    
    