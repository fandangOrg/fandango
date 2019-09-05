'''
Created on 30 apr 2019

@author: daniele
'''
import pandas as pd 
from fake_news_detection.config.AppConfig import picklepath, url_service_media, url_service_authors,\
    url_service_preprocessing, url_crawler
from ds4biz_commons.utils.requests_utils import URLRequest
from fake_news_detection.utils.logger import getLogger
import json
from fake_news_detection.model.InterfacceComunicazioni import News_raw,\
    News_DataModel, Author_org_DataModel, Media_DataModel, Topics_DataModel,\
    OutputVideoService, OutputImageService, OutputAuthorService,\
    OutputPublishService
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO, DAONewsElastic
from fake_news_detection.model.singleton_filter import Singleton
from threading import Thread
import os
import time
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains
import inspect
import random
from fake_news_detection.utils.score_utils import normalizer_neg, normalizer_pos
log = getLogger(__name__)

def log_info(f):
    def wrapped(*args, **kwargs):
        l=5
        for ff in inspect.stack():
            l=l+5
            if ff.function=='crawl_prep':break
        punti="."*l
        log.info(punti+"START:"+f.__name__)
        result = f(*args, **kwargs)
        log.info(punti+"END  :"+f.__name__)
        return result
    return wrapped



class ScrapyService:
    '''
    classdocs
    '''


    def __init__(self, url_media_service=url_service_media,url_prepocessing=url_service_preprocessing):
        '''
        Constructor
        '''
        self.url_media_service = url_media_service
        self.url_crawler=url_crawler
        self.url_prepocessing=url_prepocessing
        self.headers = {'content-type': "application/json",'accept': "application/json"}

    @log_info
    def _crawling(self,url):
        try:
            #print("CRAWLING CERTH "+url)
            u = URLRequest(self.url_crawler+"/api/retrieve_article")
            payload= {"url": url}
            j = json.dumps(payload)
            response = u.post(data=j, headers=self.headers)
            news=News_raw(**response)
            return news
        except Exception as e:
            #print(e)
            return None
    @log_info
    def _preprocessing(self,raw_news:News_raw) -> News_DataModel:
        payload = raw_news.__dict__
        ##print("payload",payload)
        #payload["fakeness" ]= ""
        u = URLRequest(self.url_prepocessing+"/preprocess/article")
        j = json.dumps(payload)
        
        ##print(j)
        response = u.post(data=j, headers=self.headers)
        #print("response",response)
        
        return News_DataModel(**response)
    @log_info
    def scrapy(self,url)-> News_DataModel:
        #print("start _crawling")
        raw_article = self._crawling(url)
        #print("start _preprocessing") 
        prepo_article = self._preprocessing(raw_article)
        prepo_article.sourceDomain=prepo_article.sourceDomain
        #prepo_article.video = ["https://www.youtube.com/watch?v=wZZ7oFKsKzY","https://www.youtube.com/watch?v=w0AOGeqOnFY"]
        return(prepo_article)

         

class AnalyticsService(metaclass=Singleton):
    '''
    classdocs
    '''


    def __init__(self, url_media_service=url_service_media,url_authors=url_service_authors):
        '''
        Constructor
        '''
        self.url_media_service = url_media_service
        self.url_authors = url_authors
        self.headers = {'content-type': "application/json",'accept': "application/json"}
        self.daopredictor = FSMemoryPredictorDAO(picklepath)
        dao = DAOTrainingElasticByDomains()
        self.dic_domains = dao.get_domains_from_elastic()
        
        #=======================================================================
        # self.nome_modello={"en":"en"}
        # for k in self.nome_modello:
        #     #print("load model",k)
        #     self.daopredictor.get_by_id(self.nome_modello.get(k,"en"))
        #=======================================================================
        self.dao =DAONewsElastic()

    def _test(self,id):
        #model =self.daopredictor.get_by_id(self.nome_modello.get(id,"en"))
        model =self.daopredictor.get_by_id(id)
    @log_info
    def _text_analysis(self,news_preprocessed:News_DataModel) -> News_DataModel:
        #print('''ANALISI NEWS IN LINGUA '''+ news_preprocessed.language)
        try:
            model =self.daopredictor.get_by_id(news_preprocessed.language)
        except:
            #print("Doesn't exist model in ",news_preprocessed.language)
            #print("I use en model")
            model =self.daopredictor.get_by_id("en")
        df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
        prest,features = model.predict_proba(df)
        #print("source_domain",news_preprocessed.sourceDomain,news_preprocessed.sourceDomain in  self.dic_domains['REAL'],self.dic_domains['REAL'] )
        
        if news_preprocessed.sourceDomain in  self.dic_domains['FAKE']:
            prest=normalizer_neg(prest)
            #prest = [[1.0,0.0]]
        elif news_preprocessed.sourceDomain in  self.dic_domains['REAL'] :
            #prest = [[0.0,1.0]]
            prest=normalizer_pos(prest)
        #print("model.predictor_fakeness.classes_",model.predictor._classes)
        #print("PREST",prest)
        prest = pd.DataFrame(prest, columns=model.predictor._classes)
        #print("PREST",prest)
        prest=pd.concat([prest,features],axis=1)
        return prest
    
    @log_info
    def _get_authors_org_ids(self,news_preprocessed:News_DataModel)-> Author_org_DataModel:
        u = URLRequest(self.url_authors+"/graph/article")
        payload = news_preprocessed.__dict__
        ##print("payload",payload)
        #payload['identifier']=payload['identifier']
        j = json.dumps(payload)
        try:
            start = time.time()
            response = u.post(data=j, headers=self.headers)
            end = time.time()
            #print("TEMPO SPESO PER LA RICHIESTA DEGLI AUTORI ==>>>",end - start)
            #print("response->",response)
            if  'error' in response:
                return Author_org_DataModel('',[],[])
            return Author_org_DataModel(**response)
        except Exception as e :
            #print("ERROR SERVICE _get_authors_org_ids: "+ str(e))
            return Author_org_DataModel('',[],[])
    @log_info     
    def _get_media_ids(self,news_preprocessed:News_DataModel, disable=True) -> Media_DataModel:
        try:
            if disable:
                return Media_DataModel('',[],[])
            #print("......start request image and video")
            u = URLRequest(self.url_media_service+"/api/media_analysis")
            payload = {"images": news_preprocessed.images,"videos": news_preprocessed.videos,"identifier": news_preprocessed.identifier}
            ##print("RICHIESTA VIDEOIMMAGINI  ",payload)
            j = json.dumps(payload)
            response = u.post(data=j, headers=self.headers)
            print("VIDEOIMMAGINI RESPOSNE",response)
            #print("......start request image and video")
            return Media_DataModel(**response)
        except Exception as e :
            #print("ERROR SERVICE MEDIA IDS:  "+str(e))
            return Media_DataModel('',[],[])
    @log_info    
    def _get_topics_ids(self,news_preprocessed:News_DataModel) -> Topics_DataModel:
        try:
            u = URLRequest(self.url_media_service+"/api/extract_topics")
            payload = {"articleBody": news_preprocessed.articleBody,
                       "headline": news_preprocessed.headline,
                       "identifier": news_preprocessed.identifier,
                       "language" : news_preprocessed.language }#####---->modify when ready from upm preprocessing 
            j = json.dumps(payload)
            response = u.post(data=j, headers=self.headers)
            return Topics_DataModel(**response)
        except Exception as e:
            print("ERROR SERVICE TOPIC",e)
            return Topics_DataModel('','', [],[])
    def _clear(self,data):
        return str(data).split(" ")[0]
    
    @log_info                            
    def _save_news(self,news_preprocessed:News_DataModel,js_t,score_fake=0.0,is_old=False):
        #print("start analyzer all component") 
        d = {"headline": news_preprocessed.headline,
            "articleBody" : news_preprocessed.articleBody,
            "dateCreated": news_preprocessed.dateCreated,
            "dateModified": news_preprocessed.dateModified,
            "datePublished": news_preprocessed.datePublished,
            "author": news_preprocessed.author,
            "publisher": news_preprocessed.publisher,
            "sourceDomain": news_preprocessed.sourceDomain,
            "calculatedRating": 0.0,
            "identifier": news_preprocessed.identifier,
            "inLanguage": news_preprocessed.language,
            "url": news_preprocessed.url,
            "publishDateEstimated":news_preprocessed.publishDateEstimated,
            "processType":"online",
            "features_text":js_t
            }
        if not self.dao.is_valitade_news_existence(news_preprocessed.identifier):
            print("trovato già")
            is_old = True
            
        #print("analizzo gli autori")
        autors_org=self._get_authors_org_ids(news_preprocessed)
        news_preprocessed.video_analizer=True
        news_preprocessed.image_analizer=True
        #print("analizza video e immagini",news_preprocessed.video_analizer,news_preprocessed.image_analizer)
        if not news_preprocessed.video_analizer:
            news_preprocessed.video=[]
        if not news_preprocessed.image_analizer:
            news_preprocessed.images=[]
        #print("analizzo i media")    
        media= self._get_media_ids(news_preprocessed)
        if not is_old:
            #print("analizzo i topic")
            tp_entity=self._get_topics_ids(news_preprocessed)
        else:
            tp_entity=Topics_DataModel('','', [],[])
        ####calculatedRatingDetail
        calculatedRatingDetail=dict()
        calculatedRatingDetail['textRating']=score_fake
        calculatedRatingDetail['authorRating']=autors_org.authorRating
        calculatedRatingDetail['publisherRating']=autors_org.publisherRating
        #print(calculatedRatingDetail['publisherRating'])
        ####
        d['calculatedRatingDetail']=calculatedRatingDetail
        d['author'] = autors_org.author
        d['publisher'] = autors_org.publisher
        #d['images'] = media.images
        d['contains'] = media.videos+ media.images
        d['mentions'] = tp_entity.mentions
        d['about'] = tp_entity.about
        d['topic'] = tp_entity.topic
        d['dateCreated'] = self._clear(news_preprocessed.dateCreated)
        d['dateModified'] =self._clear(news_preprocessed.dateModified)
        d['datePublished'] =self._clear(news_preprocessed.datePublished)
        
        if not is_old:  
            print("save")
            self.dao.create_doc_news(d)
        else:
            print("non save")
        d['images'] = media.images
        d['videos'] = media.videos
        return d
    @log_info        
    def _info_authors_and_pub_analysis(self,id_item:str,service:str)-> str:
        try:
            u = URLRequest(self.url_authors+"/"+service+"/"+id_item)
            response = u.get(headers=self.headers)
            if service=="author":
                class_response =  OutputAuthorService
            else:
                class_response = OutputPublishService
            if  'error' in response:
                print("error ",response)
                return class_response(id_item)
            
            #print("AUTORESID",id_item,response)
            return class_response(**response)
        except Exception as e :
            #print("ERROR SERVICE _info_authors_and_pub_analysis: "+str(e))
            return class_response(id_item)
    @log_info        
    def _info_video_analysis(self,id_video:str)-> str:
        try:
            u = URLRequest(self.url_media_service+"/api/analyze_video/"+id_video)
            response = u.get(headers=self.headers)
            ##print("INFOvideo->",u,response)
            if  'error' in response:
                return  {'identifier':id_video}# OutputVideoService(id_video)
            #info_video=OutputVideoService(**response)
            return response
        #info_video
        except:
            #print("ERROR SERVICE _info_video_analysis")
            return {'identifier':id_video}
        #OutputVideoService(id_video)
    @log_info    
    def _info_image_analysis(self,id_image)-> str: 
        try:
            u = URLRequest(self.url_media_service+"/api/analyze_image/"+id_image)
            response = u.get(headers=self.headers)
#            #print("INFOIMAGE->",response)
            if  'error' in response:
                #print("INFOIMAGE_ERRORE->",response)
                return {'identifier':id_image}
            #response 
            #OutputImageService(id_image)
            #info_image=OutputImageService(**response)
            return response
        #info_image
        except:
            #print("ERROR SERVICE _info_image_analysis",id_image)
            return {'identifier':id_image}
         #OutputImageService(id_image)   
    @log_info
    def analyzer(self,news_preprocessed:News_DataModel,save=True,old=False) -> str:
        #print("start analyzer")
        pd_text=self._text_analysis(news_preprocessed)
        js_t=json.loads(pd_text.to_json(orient='records'))
        if save:
            
            list_authors=[]
            list_publishs=[]
            list_images=[]
            list_videos=[]
            score=pd_text[1][0]
            news=self._save_news(news_preprocessed,js_t,score,old)
            ##
            #
            #
            #===================================================================
            # for image in news['images']:
            #     list_images.append(self._info_image_analysis(image))
            # ##    
            # for video in news['videos']:
            #     list_videos.append(self._info_video_analysis(video))
            # 
            #===================================================================
            #
            #
            ##print("NEWS-->>",news)
                
            #print("start _info_authors_and_pub_analysis")
            for authos in news['author']:
                #print(authos,self._info_authors_and_pub_analysis(authos, 'author').__dict__)
                list_authors.append(self._info_authors_and_pub_analysis(authos, 'author').__dict__)
            #print("start _info_authors_and_pub_analysis")
            for organization in news['publisher']:
                list_publishs.append(self._info_authors_and_pub_analysis(organization, 'organization').__dict__)
            
            #pd_video=pd.DataFrame(list_videos)
            #pd_image=pd.DataFrame(list_images)
            pd_authors=pd.DataFrame(list_authors)
            pd_publish=pd.DataFrame(list_publishs)
            #js_V=json.loads(pd_video.to_json(orient='records'))
            #js_i=json.loads(pd_image.to_json(orient='records'))
            js_a=json.loads(pd_authors.to_json(orient='records'))
            js_p=json.loads(pd_publish.to_json(orient='records'))


            #return {"text":js_t,"videos":js_V,"images":js_i,"authors":js_a,"publishers":js_p} 
            return {"text":js_t, "authors":js_a,"publishers":js_p} 

        else:      
            return pd_text,js_t  
         
def running(name):
    #print("name", name)
    a = AnalyticsService()
    b = AnalyticsService()
    #print("nstopo", a._test('en'))
    #print("nstopo", a._test('en'))

    
if __name__ == '__main__':
    service_scrapy=ScrapyService()
    service_analyzer= AnalyticsService()
    news_preprocessed=service_scrapy.scrapy("https://www.theguardian.com/us-news/2019/feb/19/bernie-sanders-announces-2020-run-presidency")
    prest=service_analyzer.analyzer(news_preprocessed)
    
    headers = {'content-type': "application/json",'accept': "application/json"}
#===============================================================================
#     u = URLRequest(url_service_certh+"/api/media_analysis")
#     payload = {"images": ["https://i.guim.co.uk/img/media/fc33d72d0d06b2b08d2c8e6c8ccc5879bbdb7b3d/5_343_2662_1597/master/2662.jpg?width=300&quality=85&auto=format&fit=max&s=3e45e12e82a20bc9a70c001854b44f67"],"videos": [""],"identifier": "test"}
#     #print("RICHIESTA VIDEOIMMAGINI  ",payload)
# 
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     #print("VIDEOIMMAGINI RESPOSNE",response)
#===============================================================================
    text='''
They urged swift action after the first deadly 737 Max crash off Indonesia in October, according to audio obtained by CBS and the New York Times.

Boeing reportedly resisted their calls but promised a software fix.

But this had not been rolled out when an Ethiopian Airlines' 737 Max crashed four months later, killing 157 people.

Currently 737 Max planes are grounded worldwide amid concerns that an anti-stall system may have contributed to both crashes.

Boeing is in the process of updating the system, known as MCAS, but denies it was solely to blame for the disasters.

    Boeing admits knowing of 737 Max problem
    Boeing safety system not at fault, says chief executive
    Boeing 737 Max: What went wrong?

In a closed door meeting with Boeing executives last November, which was secretly recorded, American Airlines' pilots can be heard expressing concerns about the safety of MCAS.

Boeing vice-president Mike Sinnett told the pilots: "No one has yet to conclude that the sole cause of this was this function on the airplane."

Later in the meeting, he added: "The worst thing that can ever happen is a tragedy like this, and the even worse thing would be another one."

The pilots also complained they had not been told about MCAS, which was new to the 737 Max, until after the Lion Air crash off Indonesia, which killed 189.

"These guys didn't even know the damn system was on the airplane, nor did anybody else," said Mike Michaelis, head of safety for the pilots' union.

Boeing declined to comment on the November meeting, saying: "We are focused on working with pilots, airlines and global regulators to certify the updates on the Max 

'''
    #===========================================================================
    # u = URLRequest(url_service_certh+"/api/extract_topics")
    # payload = {"articleBody": text,
    #            "headline": text,
    #            "identifier": "test",
    #            "language" : "en" }#####---->modify when ready from upm preprocessing 
    # j = json.dumps(payload)
    # response = u.post(data=j, headers=headers)
    # #print(response)
    #===========================================================================
    #===========================================================================
    # #print(os.environ)
    # if 'TREETAGGER' in os.environ:
    #     founddir = os.environ['TREETAGGER']
    # elif 'TREETAGGER_HOME' in os.environ:
    #     founddir = os.environ['TREETAGGER_HOME']
    #===========================================================================
    