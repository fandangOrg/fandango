'''
Created on 11 mar 2019

@author: camila
'''

from fake_news_detection.utils.logger import getLogger
from brokermanager.model.publishers import KafkaPublisher
from fake_news_detection.model.InterfacceComunicazioni import News_DataModel
from fake_news_detection.business.Pipeline import AnalyticsService
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains
import pandas as pd


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
        
    def do(self,msg,dic_domains):
                global c
                c+=1
                if c%100==0:
                    print(c)
                
                news_preprocessed = News_DataModel(**msg)
                #if msg['language'] != 'en':return
                #print(msg['headline'])
                #print(msg['articleBody'])
                output,js_t=self.analytics.analyzer(news_preprocessed,False) 
                output = str(output[1][0])
                
                try:
                    model =self.analytics.daopredictor.get_by_id(msg['language'])
                except:
                    model = None
                    
                if model:
                    #l=[{'title': msg['headline'], 'text':msg['articleBody'] ,'label': 1}]
                    #df = pd.DataFrame(l)
                    #model.partial_fit(df)
                    if msg['sourceDomain'] in dic_domains['FAKE']: 
                        l=[{'title': msg['headline'], 'text':msg['articleBody'] ,'label': 1}]
                        #dict_for_training = {'text':msg['articleBody'], 'title':msg['headline'], 'label' :'FAKE', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                        testo=msg['identifier']+"\t"+msg['sourceDomain']+"\tFAKE\t"+msg['language']+"\t"+msg['headline']+"\t"+msg['articleBody']
                        #df = pd.DataFrame(l)
                        #model.partial_fit(df)
                        testo=testo.replace("\n","$##$")
                        #file_output.write(testo+"\n")
                        print("add negative fit",msg['sourceDomain'] )
                        #output = 0.0
                        #={'text':msg['articleBody'], 'title':msg['headline'], 'label' :'FAKE', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                    elif msg['sourceDomain'] in dic_domains['REAL']:
                        testo=msg['identifier']+"\t"+msg['sourceDomain']+"\tREAL\t"+msg['language']+"\t"+msg['headline']+"\t"+msg['articleBody']
                        testo=testo.replace("\n","$##$")
                        #file_output.write(testo+"\n")
                        #l=[{'title': msg['headline'], 'text':msg['articleBody'] ,'label':0}]
                        #df = pd.DataFrame(l)
                        #model.partial_fit(df)
                        print("add  positive fit",msg['sourceDomain'] )
                        #output = 1.0
                print( msg['sourceDomain'],msg['language'],output)
                #dict_for_training = {'text':msg['articleBody'], 'title': msg['headline'], 'label' : 'REAL', 'sourceDomian':msg['sourceDomain'],'language' : msg['language'], 'identifier': msg['identifier']}
                #print("dict_output",dict_output)
                dict_output = {"identifier":msg['identifier'], 
                               "headline":msg['headline'],
                               "articleBody": msg['articleBody'],
                               "dateCreated": msg['dateCreated'], 
                               "dateModified" : msg['dateModified'], 
                               "datePublished":msg['datePublished'],
                               "url":msg['url'],
                               "textRating": output,
                               "publishDateEstimated" : news_preprocessed.publishDateEstimated,
                               "sourceDomain": news_preprocessed.sourceDomain, 
                               "inLanguage": news_preprocessed.language,
                               "features_text":js_t                      
                                #"publishDateEstimate" : ""
                             }
                try:
                    #msg['publishDateEstimate']
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
