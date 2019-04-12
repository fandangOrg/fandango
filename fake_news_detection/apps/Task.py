'''
Created on 11 mar 2019

@author: camila
'''

from brokermanager.model.consumers import ConsumerTask
from kafka.producer.kafka import KafkaProducer
from fake_news_detection.utils.logger import getLogger
from kafka.consumer.group import KafkaConsumer
import logging, time, json
from fake_news_detection.utils.Exception import FandangoException
from brokermanager.model.publishers import KafkaPublisher
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.business.Analyzer import analyzer, log
from numpy.lib.utils import source


log = getLogger(__name__)

class Task:
    def do(self,msg):
        raise NotImplemented
    
class Task_1(Task):
    def __init__(self,publisher:KafkaPublisher,topic,*arg,**args):
        self.publisher = publisher
        self.topic=topic
        
        
        self.daopredictor = FSMemoryPredictorDAO(picklepath)
    
        
    def do(self,msg):
        print("applico l'analizer e trovo lo score di ",msg)
        #id_document
        #score_ml %
        info_news = InterfaceInputModel(title=msg["headline"], text = msg["articleBody"], source = msg['publisher'])
        nome_modello="english_try_version"
        output= analyzer(info_news,self.daopredictor,nome_modello) 
        print(output)
        dict_output = {"id_news":msg['id_news'],"calculatedRating":output, "headline":msg['headline'],"articleBody": msg['articleBody'],"dateCreated": msg['dateCreated'], "dateModified" : msg['dateModified'], "datePublished":msg['datePublished']}
        print(dict_output)
        try:
            self.publisher.publish(self.topic, dict_output)
            print("document added to the kafka topic")
        except:
            log.error("document not added")
            #self.publisher.push("")        
        
                 


if __name__ == '__main__':
    
    pass
    '''
    c = Task_1(topic="test_lvt" , group_id="cami", bootstrap_servers=["localhost:9092"])
    c.do()      
    '''
