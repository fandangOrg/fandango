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
import csv 
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains

log = getLogger(__name__)
c=0
class Task:
    def do(self,msg):
        raise NotImplemented
    
class Task_Analyzer(Task):
    def __init__(self,publisher:KafkaPublisher,topic,**args):
        self.analytics=AnalyticsService()
        self.publisher = publisher
        self.topic=topic
        
    def do(self,msg,file_output,dic_domains):
                global c
                c+=1
                if c%100==0:
                    print(c)
                
                #fieldnames = ['identifier', 'text', 'title','label','sourceDomian','language']
                #writer = csv.DictWriter(file_output, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL,fieldnames = fieldnames)
                #print("applico l'analizer e trovo lo score di ",msg)
                news_preprocessed = News_DataModel(language=msg.get('language','en'),headline= msg["headline"], articleBody = msg["articleBody"], sourceDomain = msg['sourceDomain'],identifier = msg['identifier'], dateCreated = msg['dateCreated'] , dateModified= msg['dateModified'], datePublished = msg['datePublished'], author = msg['author'], publisher = msg['publisher'], calculateRating = msg['calculateRating'], calculateRatingDetail = msg['calculateRatingDetail'], images = msg['images'], videos = msg['videos'])
                if msg['language'] != 'en':return
                
                #print(msg['headline'])
                #print(msg['articleBody'])
                output = 'hey'
                
                output=self.analytics.analyzer(news_preprocessed,False) 
                output = output[1][0]
                print( msg['sourceDomain'],msg['language'],output)
                
       
                
                if msg['sourceDomain'] in dic_domains['FAKE']: 
                    #dict_for_training = {'text':msg['articleBody'], 'title':msg['headline'], 'label' :'FAKE', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                    testo=msg['identifier']+"\t"+msg['sourceDomain']+"\tFAKE\t"+msg['language']+"\t"+msg['headline']+"\t"+msg['articleBody']
                    testo=testo.replace("\n","$##$")
                    file_output.write(testo+"\n")
                    print("add negative",msg['sourceDomain'] )
                    output = 0.0
                    #={'text':msg['articleBody'], 'title':msg['headline'], 'label' :'FAKE', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                elif msg['sourceDomain'] in dic_domains['REAL']:
                    testo=msg['identifier']+"\t"+msg['sourceDomain']+"\tREAL\t"+msg['language']+"\t"+msg['headline']+"\t"+msg['articleBody']
                    testo=testo.replace("\n","$##$")
                    file_output.write(testo+"\n")
                    output = 1.0
                    print("add  pos",msg['sourceDomain'] )
                    #dict_for_training = {'text':msg['articleBody'], 'title': msg['headline'], 'label' : 'REAL', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                #print("dict_output",dict_output)
                dict_output = {"identifier":msg['identifier'], "headline":msg['headline'],
                               "articleBody": msg['articleBody'],
                               "dateCreated": msg['dateCreated'], 
                               "dateModified" : msg['dateModified'], 
                               "datePublished":msg['datePublished'],
                                "textRating": output
                             }
                try:
                    #self.file_output
                    self.publisher.publish(self.topic, dict_output)
                    #print("document added to the kafka topic")
                except Exception as e:
                    log.error("document not added",e)
                    #self.publisher.push("")      
        
                 


if __name__ == '__main__':
    
    dao = DAOTrainingElasticByDomains()
    dic_domains = dao.get_domains_from_elastic()
    print(dic_domains)
        
    '''
    c = Task_1(topic="test_lvt" , group_id="cami", bootstrap_servers=["localhost:9092"])
    c.do()      
    '''
