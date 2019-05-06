'''
Created on 30 apr 2019

@author: daniele
'''
import pandas as pd 
from fake_news_detection.config.AppConfig import url_service_certh,\
    url_service_upm, picklepath
from ds4biz_commons.utils.requests_utils import URLRequest
from fake_news_detection.utils.logger import getLogger
import json
from fake_news_detection.model.InterfacceComunicazioni import News_raw,\
    News_DataModel, Author_org_DataModel, Media_DataModel, Topics_DataModel,\
    OutputVideoService, OutputImageService
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO, DAONewsElastic
from fake_news_detection.model.singleton_filter import Singleton
from threading import Thread
import os
log = getLogger(__name__)

class ScrapyService:
    '''
    classdocs
    '''


    def __init__(self, url_media_service=url_service_certh,url_prepocessing=url_service_upm):
        '''
        Constructor
        '''
        self.url_media_service = url_media_service
        self.url_prepocessing=url_prepocessing
        self.headers = {'content-type': "application/json",'accept': "application/json"}

    
    def _crawling(self,url):
        log.info("CRAWLING CERTH "+url)
        u = URLRequest(self.url_media_service+"/api/retrieve_article")
        payload= {"url": url}
        j = json.dumps(payload)
        response = u.post(data=j, headers=self.headers)
        news=News_raw(**response)
        print("VIDEO->",news.videos)
        print("IMMAGINI->",news.images)
        return news
    
    
    def _preprocessing(self,raw_news:News_raw) -> News_DataModel:
        payload = raw_news.__dict__
        payload["fakeness" ]= ""
        u = URLRequest(self.url_prepocessing+"/preprocess/article")
        j = json.dumps(payload)
        response = u.post(data=j, headers=self.headers)
        return News_DataModel(**response)

    def scrapy(self,url)-> News_DataModel:
        raw_article = self._crawling(url) 
        prepo_article = self._preprocessing(raw_article)
        prepo_article.sourceDomain=[prepo_article.sourceDomain]
        return(prepo_article)

         

class AnalyticsService(metaclass=Singleton):
    '''
    classdocs
    '''


    def __init__(self, url_media_service=url_service_certh,url_authors=url_service_upm):
        '''
        Constructor
        '''
        self.url_media_service = url_media_service
        self.url_authors = url_authors
        self.headers = {'content-type': "application/json",'accept': "application/json"}
        self.daopredictor = FSMemoryPredictorDAO(picklepath)
        self.nome_modello={"en":"english_try1_version"}
        for k in self.nome_modello:
            print("load model",k)
            self.daopredictor.get_by_id(self.nome_modello.get(k,"english_try1_version"))
        self.dao =DAONewsElastic()

    def _test(self,id):
        model =self.daopredictor.get_by_id(self.nome_modello.get(id,"english_try1_version"))
        
    def _text_analysis(self,news_preprocessed:News_DataModel) -> News_DataModel:
        log.info('''ANALISI NEWS IN LINGUA '''+ news_preprocessed.language)
        model =self.daopredictor.get_by_id(self.nome_modello.get(news_preprocessed.language,"english_try1_version"))
        df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
        prest,features = model.predict_proba(df)
        prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
        prest=pd.concat([prest,features],axis=1)
        return prest
    
    def _get_authors_org_ids(self,news_preprocessed:News_DataModel)-> Author_org_DataModel:
        u = URLRequest(self.url_authors+"/graph/article")
        payload = news_preprocessed.__dict__
        j = json.dumps(payload)
        response = u.post(data=j, headers=self.headers)
        print("response->",response)
        if  'error' in response:
            return Author_org_DataModel('',[],[])
        return Author_org_DataModel(**response)
        
    def _get_media_ids(self,news_preprocessed:News_DataModel) -> Media_DataModel:
        
        u = URLRequest(self.url_media_service+"/api/media_analysis")
        payload = {"images": news_preprocessed.images,"videos": news_preprocessed.video,"identifier": news_preprocessed.identifier}
        j = json.dumps(payload)
        response = u.post(data=j, headers=self.headers)
        #response['identifier'] = news_preprocessed.identifier
        return Media_DataModel(**response)
    
    def _get_topics_ids(self,news_preprocessed:News_DataModel) -> Topics_DataModel:
        u = URLRequest(self.url_media_service+"/api/extract_topics")
        payload = {"articleBody": news_preprocessed.articleBody,
                   "headline": news_preprocessed.headline,
                   "identifier": news_preprocessed.identifier,
                   "language" : "language" }#####---->modify when ready from upm preprocessing 
        j = json.dumps(payload)
        response = u.post(data=j, headers=self.headers)
        return Topics_DataModel(**response)


    def _clear(self,data):
        return str(data).split(" ")[0]
                                
    def _save_news(self,news_preprocessed:News_DataModel,score_fake=0.0):
        d = {"headline": news_preprocessed.headline,
            "articleBody" : news_preprocessed.articleBody,
            "dateCreated": news_preprocessed.dateCreated,
            "dateModified": news_preprocessed.dateModified,
            "datePublished": news_preprocessed.datePublished,
            "author": news_preprocessed.author,
            "publisher": news_preprocessed.publisher,
            "sourceDomain": news_preprocessed.sourceDomain,
            "calculatedRatingDetail": news_preprocessed.calculateRatingDetail,
            "calculatedRating": score_fake,
            "identifier": news_preprocessed.identifier}
    
        autors_org=self._get_authors_org_ids(news_preprocessed)
        news_preprocessed.video_analizer=True
        news_preprocessed.image_analizer=True
        print("analizza video e immagini",news_preprocessed.video_analizer,news_preprocessed.image_analizer)
        if not news_preprocessed.video_analizer:
            news_preprocessed.video=[]
        if not news_preprocessed.image_analizer:
            news_preprocessed.images=[]
            
        media= self._get_media_ids(news_preprocessed)
        tp_entity=self._get_topics_ids(news_preprocessed)
        d['author'] = autors_org.author
        d['publisher'] = autors_org.publisher
        #d['images'] = media.images
        d['contains'] = media.videos+ media.images
        d['mentions'] = tp_entity.mentions
        d['about'] = tp_entity.about
        d['dateCreated'] = self._clear(news_preprocessed.dateCreated)
        d['dateModified'] =self._clear(news_preprocessed.dateModified)
        d['datePublished'] =self._clear(news_preprocessed.datePublished)
        self.dao.create_doc_news(d)
        d['images'] = media.images
        d['videos'] = media.videos
        return d
            
            
    def _info_video_analysis(self,id_video:str)-> str:
        u = URLRequest(self.url_media_service+"/api/analyze_video/"+id_video)
        response = u.get(headers=self.headers)
        if  'error' in response:
            return OutputVideoService(id_video)
        info_video=OutputVideoService(**response)
        return info_video
    
    
    def _info_image_analysis(self,id_image)-> str:
        u = URLRequest(self.url_media_service+"/api/analyze_image/"+id_image)
        response = u.get(headers=self.headers)
        print(u)
        print(response)
        if  'error' in response:
            return OutputImageService(id_image)
        info_image=OutputImageService(**response)
        return info_image
    
 
    def analyzer(self,news_preprocessed:News_DataModel,save=True) -> str:
        pd_text=self._text_analysis(news_preprocessed)
        if save:
            list_images=[]
            list_videos=[]
            score=pd_text['REAL'][0]
            news=self._save_news(news_preprocessed,score)
            ##
            for image in news['images']:
                list_images.append(self._info_image_analysis(image).__dict__)
            ##    
            for video in news['videos']:
                list_videos.append(self._info_video_analysis(video).__dict__)
            ##
            pd_video=pd.DataFrame(list_videos)
            pd_image=pd.DataFrame(list_images)
            js_t=json.loads(pd_text.to_json(orient='records'))
            js_V=json.loads(pd_video.to_json(orient='records'))
            js_i=json.loads(pd_image.to_json(orient='records'))
            return {"text":js_t,"videos":js_V,"images":js_i} 
        else:      
            return pd_text
         
def running(name):
    print("name", name)
    a = AnalyticsService()
    b = AnalyticsService()
    print("nstopo", a._test('en'))
    print("nstopo", a._test('en'))

    
if __name__ == '__main__':
    print(os.environ)
    if 'TREETAGGER' in os.environ:
        founddir = os.environ['TREETAGGER']
    elif 'TREETAGGER_HOME' in os.environ:
        founddir = os.environ['TREETAGGER_HOME']
    