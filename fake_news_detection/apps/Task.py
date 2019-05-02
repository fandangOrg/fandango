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
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel,\
    News_DataModel
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.business.Analyzer import analyzer, log
from numpy.lib.utils import source
from fake_news_detection.business.Pipeline import AnalyticsService


log = getLogger(__name__)

class Task:
    def do(self,msg):
        raise NotImplemented
    
class Task_Analyzer(Task):
    def __init__(self,publisher:KafkaPublisher,topic,**args):
        self.publisher = publisher
        self.topic=topic
        self.analytics= AnalyticsService()
        
    def do(self,msg):
        print("applico l'analizer e trovo lo score di ",msg)
        news_preprocessed = News_DataModel(language=msg.get('language','en'),headline= msg["headline"], articleBody = msg["articleBody"], sourceDomain = msg['sourceDomain'],identifier = msg['identifier'], dateCreated = msg['dateCreated'] , dateModified= msg['dateModified'], datePublished = msg['datePublished'], author = msg['author'], publisher = msg['publisher'], calculateRating = msg['calculateRating'], calculateRatingDetail = msg['calculateRatingDetail'], images = msg['images'], video = msg['video'])
        print(msg['headline'])
        print(msg['articleBody'])
        output=self.analytics.analyzer(news_preprocessed,False) 
        print(output)
        output = output['REAL'][0]
        print(output)
        dict_output = {"identifier":msg['identifier'],"calculatedRating": output, "headline":msg['headline'],"articleBody": msg['articleBody'],"dateCreated": msg['dateCreated'], "dateModified" : msg['dateModified'], "datePublished":msg['datePublished'],"calculatedRatingDetail":msg['calculateRatingDetail'], "images" : msg['images'], "videos":msg['video']}
        print("dict_output",dict_output)
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
