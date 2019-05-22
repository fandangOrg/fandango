'''
Created on 30 apr 2019

@author: daniele
'''
import pandas as pd 
from fake_news_detection.config.AppConfig import picklepath, url_service_media, url_service_authors,\
    url_service_preprocessing
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
log = getLogger(__name__)

class ScrapyService:
    '''
    classdocs
    '''


    def __init__(self, url_media_service=url_service_authors,url_prepocessing=url_service_preprocessing):
        '''
        Constructor
        '''
        self.url_media_service = url_media_service
        self.url_prepocessing=url_prepocessing
        self.headers = {'content-type': "application/json",'accept': "application/json"}

    
    def _crawling(self,url):
        try:
            print("CRAWLING CERTH "+url)
            u = URLRequest(self.url_media_service+"/api/retrieve_article")
            payload= {"url": url}
            j = json.dumps(payload)
            response = u.post(data=j, headers=self.headers)
            news=News_raw(**response)
            print("VIDEO->",news.videos)
            print("IMMAGINI->",news.images)
            return news
        except:
            return None
    
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
        self.nome_modello={"en":"english_try1_version"}
        for k in self.nome_modello:
            print("load model",k)
            self.daopredictor.get_by_id(self.nome_modello.get(k,"english_try1_version"))
        self.dao =DAONewsElastic()

    def _test(self,id):
        model =self.daopredictor.get_by_id(self.nome_modello.get(id,"english_try1_version"))
        
    def _text_analysis(self,news_preprocessed:News_DataModel) -> News_DataModel:
        print('''ANALISI NEWS IN LINGUA '''+ news_preprocessed.language)
        model =self.daopredictor.get_by_id(self.nome_modello.get(news_preprocessed.language,"english_try1_version"))
        df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
        prest,features = model.predict_proba(df)
        prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
        prest=pd.concat([prest,features],axis=1)
        return prest
    
    def _get_authors_org_ids(self,news_preprocessed:News_DataModel)-> Author_org_DataModel:
        u = URLRequest(self.url_authors+"/graph/article")
        payload = news_preprocessed.__dict__
        payload['identifier']=payload['identifier'][0]
        j = json.dumps(payload)
        print(j)
        try:
            response = u.post(data=j, headers=self.headers)
            print("response->",response)
            if  'error' in response:
                return Author_org_DataModel('',[],[])
            return Author_org_DataModel(**response)
        except Exception as e :
            print("ERROR SERVICE _get_authors_org_ids: "+ str(e))
            return Author_org_DataModel('',[],[])
         
    def _get_media_ids(self,news_preprocessed:News_DataModel) -> Media_DataModel:
        try:
            u = URLRequest(self.url_media_service+"/api/media_analysis")
            payload = {"images": news_preprocessed.images,"videos": news_preprocessed.video,"identifier": news_preprocessed.identifier}
            print("RICHIESTA VIDEOIMMAGINI  ",payload)

            j = json.dumps(payload)
            response = u.post(data=j, headers=self.headers)
            print("VIDEOIMMAGINI RESPOSNE",response)
            return Media_DataModel(**response)
        except Exception as e :
            print("ERROR SERVICE MEDIA IDS:  "+str(e))
            return Media_DataModel('',[],[])
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
        except:
            print("ERROR SERVICE TOPIC")
            return Topics_DataModel('',[],[])

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
            "calculatedRatingDetail": {"key":"value"},
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
        
        if self.dao.is_valitade_news_existence(news_preprocessed.identifier):
            self.dao.create_doc_news(d)
        d['images'] = media.images
        d['videos'] = media.videos
        
        
        return d
            
            
    def _info_video_analysis(self,id_video:str)-> str:
        try:
            u = URLRequest(self.url_media_service+"/api/analyze_video/"+id_video)
            response = u.get(headers=self.headers)
            print("INFOvideo->",u,response)
            if  'error' in response:
                return OutputVideoService(id_video)
            info_video=OutputVideoService(**response)
            return info_video
        except:
            print("ERROR SERVICE _info_video_analysis")
            return OutputVideoService(id_video)
    #138.4.47.33:5006/author/<author_id>
    
    def _info_authors_and_pub_analysis(self,id_item:str,service:str)-> str:
        try:
            u = URLRequest(self.url_authors+"/"+service+"/"+id_item)
            response = u.get(headers=self.headers)
            if service=="author":
                class_response =  OutputAuthorService
            else:
                class_response = OutputPublishService
            print("AUTORESID",id_item,response)
    
    
            if  'error' in response:
                return class_response(id_item)
            return class_response(**response)
        except Exception as e :
            print("ERROR SERVICE _info_authors_and_pub_analysis: "+str(e))
            return class_response(id_item)
        
        
        
    def _info_image_analysis(self,id_image)-> str: 
        try:
            u = URLRequest(self.url_media_service+"/api/analyze_image/"+id_image)
            response = u.get(headers=self.headers)
            print(u)
            print("INFOIMAGE->",response)
            if  'error' in response:
                print("INFOIMAGE_ERRORE->",response)
                return OutputImageService(id_image)
            info_image=OutputImageService(**response)
            return info_image
        except:
            print("ERROR SERVICE _info_image_analysis",id_image)
            return OutputImageService(id_image)   
 
    def analyzer(self,news_preprocessed:News_DataModel,save=True) -> str:
        pd_text=self._text_analysis(news_preprocessed)
        if save:
            
            list_authors=[]
            list_publishs=[]
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
            
            print("NEWS-->>",news)
            for authos in news['author']:
                
                list_authors.append(self._info_authors_and_pub_analysis(authos, 'author').__dict__)
            
            for organization in news['publisher']:
                list_publishs.append(self._info_authors_and_pub_analysis(organization, 'organization').__dict__)
            
            pd_video=pd.DataFrame(list_videos)
            pd_image=pd.DataFrame(list_images)
            pd_authors=pd.DataFrame(list_authors)
            print(list_authors)
            print(pd_authors)
            pd_publish=pd.DataFrame(list_publishs)
            js_t=json.loads(pd_text.to_json(orient='records'))
            js_V=json.loads(pd_video.to_json(orient='records'))
            js_i=json.loads(pd_image.to_json(orient='records'))
            js_a=json.loads(pd_authors.to_json(orient='records'))
            js_p=json.loads(pd_publish.to_json(orient='records'))


            return {"text":js_t,"videos":js_V,"images":js_i,"authors":js_a,"publishers":js_p} 
        else:      
            return pd_text
         
def running(name):
    print("name", name)
    a = AnalyticsService()
    b = AnalyticsService()
    print("nstopo", a._test('en'))
    print("nstopo", a._test('en'))

    
if __name__ == '__main__':
    headers = {'content-type': "application/json",'accept': "application/json"}
#===============================================================================
#     u = URLRequest(url_service_certh+"/api/media_analysis")
#     payload = {"images": ["https://i.guim.co.uk/img/media/fc33d72d0d06b2b08d2c8e6c8ccc5879bbdb7b3d/5_343_2662_1597/master/2662.jpg?width=300&quality=85&auto=format&fit=max&s=3e45e12e82a20bc9a70c001854b44f67"],"videos": [""],"identifier": "test"}
#     print("RICHIESTA VIDEOIMMAGINI  ",payload)
# 
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     print("VIDEOIMMAGINI RESPOSNE",response)
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
    u = URLRequest(url_service_certh+"/api/extract_topics")
    payload = {"articleBody": text,
               "headline": text,
               "identifier": "test",
               "language" : "en" }#####---->modify when ready from upm preprocessing 
    j = json.dumps(payload)
    response = u.post(data=j, headers=headers)
    print(response)
    #===========================================================================
    # print(os.environ)
    # if 'TREETAGGER' in os.environ:
    #     founddir = os.environ['TREETAGGER']
    # elif 'TREETAGGER_HOME' in os.environ:
    #     founddir = os.environ['TREETAGGER_HOME']
    #===========================================================================
    