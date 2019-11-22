'''
Created on 23 apr 2019

@author: camila
'''

from fake_news_detection.model.InterfacceComunicazioni import News_DataModel, Author_org_DataModel, Media_DataModel, Topics_DataModel,\
 InterfaceInputFeedBack, Claim_input, Claim_output, News, News_annotated,\
    Open_Data, UploadImageInput
from ds4biz_commons.utils.requests_utils import URLRequest
from fake_news_detection.config.AppConfig import  static_folder, url_service_media,\
    url_service_authors, url_similar_claims, template_path, url_upload_image
import json
from flask_cors.extension import CORS
from ds4biz_flask.model.ds4bizflask import DS4BizFlask
from fake_news_detection.config import AppConfig
from typing import List
import requests
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.model.Language import Language
from fake_news_detection.business.Pipeline import ScrapyService,\
    AnalyticsService
from fake_news_detection.apps.daemon import daemon_run
from fake_news_detection.config.constants import LABEL_SCORE
from flask.templating import render_template
from fake_news_detection.dao.DaoAnnotation import DAOElasticAnnotation
from flask.globals import request
#from fake_news_detection.apps.daemon import daemon_run


log = getLogger(__name__)
service_scrapy=ScrapyService()
service_analyzer=AnalyticsService()
###run deamon()  uncomment if you want to start kafka deamon#
#daemon_run()

headers = {'content-type': "application/json",'accept': "application/json"}

def info_score(label:str) -> str:     
    return LABEL_SCORE.get(label)

def start_daemon() -> str:
    daemon_run()
    return "done"

def analyzer(news_preprocessed:News_DataModel) -> str:
    log.info('''ANALISI NEWS'''+str(news_preprocessed.sourceDomain))
    prest=service_analyzer.analyzer(news_preprocessed)
    
    print(prest)
    #log.info(json.loads(prest))
    return prest

def get_opendata(opendata:Open_Data) -> list:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_similar_claims+"/fandango/v0.1/siren/FindFact")
    log.info("open data sent for:"+ str(opendata.text))
    payload = {"text": opendata.text ,"category": opendata.category,"topics": opendata.topics}
    print("OPEND DATA REQUEST:  ",payload)
    j = json.dumps(payload)
    req = u.post(data=j, headers= headers)
    print(req)
    return req['results']

def get_languages() -> List[Language]:
    l= list()
    l.append(Language("en","English","True"))
    l.append(Language("it","Italian","True"))
    l.append(Language("es","Spanish","True"))
    return l

def feedback(info:InterfaceInputFeedBack) -> str:
    log.info(info)
    return "OK"




class request_craw():
    def __init__(self,url:str,old:str=False):
        self.url = url
        self.old = old

def crawl_prep(url:str,old:str="False") -> News_DataModel:
    if old =="False":
        old=False
    else: 
        old = True
    print("old",old,"url",url)
    news_preprocessed= service_scrapy.scrapy(url)
    prest=service_analyzer.analyzer(news_preprocessed,old=old)
    news_preprocessed.results=prest
    news_preprocessed.similarnews = similar_news(news_preprocessed.identifier)
    topics = []
    #topics = topics_getter(news_preprocessed)
    opendata = Open_Data(text=news_preprocessed.headline, category=news_preprocessed.headline, topics= topics)
    op = get_opendata(opendata)
    prest = {"news_preprocessed": news_preprocessed , "opendata" : op}
    print(prest)
    return prest


def ping_image(id:str) -> News_DataModel:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/analyze_image/"+id)
    return u.get(headers=headers)

def ping_video(id:str) -> str:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/analyze_video/"+id)
    return u.get(headers=headers)

def upload_image(uploadimagein:UploadImageInput) -> str:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_upload_image+"/api/analyze_image")
    payload = {"url": uploadimagein.url,"force" :"true","image": uploadimagein.image}
    print("UPLOAD IMAGE REQUEST  ",payload)
    j = json.dumps(payload)
    return u.post(data=j, headers= headers)



      
def url_image_score(url:str) -> str:
    
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/media_analysis")
    payload = {"images": [url],"videos": [],"identifier": ['unkwon']}
    print("RICHIESTA IMMAGINI  ",payload)
    j = json.dumps(payload)
    return u.post(data=j, headers= headers)

def url_video_score(url:str) -> str:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/media_analysis")
    payload = {"images": [],"videos": [url],"identifier": ['unkwon']}
    print("RICHIESTA VIDEO  ",payload)
    j = json.dumps(payload)
    return u.post(data=j, headers= headers)


def author_org_getter(news_preprocessed:News_DataModel) -> Author_org_DataModel:
    
    payload = {"headline": news_preprocessed.headline,
               "articleBody" : news_preprocessed.articleBody,
               "dateCreated": news_preprocessed.dateCreated,
               "dateModified": news_preprocessed.dateModified,
               "datePublished": news_preprocessed.datePublished,
               "author": news_preprocessed.author,
               "publisher": news_preprocessed.publisher,
               "images": news_preprocessed.images,
               "video": news_preprocessed.video,
               "sourceDomain": news_preprocessed.sourceDomain,
               "calculateRatingDetail": news_preprocessed.calculateRatingDetail,
               "calculateRating": -news_preprocessed.calculateRating,
               "identifier": news_preprocessed.identifier}

    u = URLRequest(url_service_authors+"/graph/article")
    
    j = json.dumps(payload)
    headers = {'content-type': "application/json",'accept': "application/json"}
    
    response = u.post(data=j, headers=headers)
    return Author_org_DataModel(**response)


def media_getter(news_preprocessed:News_DataModel) -> Media_DataModel :
    
    u = URLRequest(url_service_media+"/api/media_analysis")
    payload = {"images": news_preprocessed.images,"videos": news_preprocessed.video,"identifier": news_preprocessed.identifier}
    j = json.dumps(payload)
    headers = {'content-type': "application/json",'accept': "application/json"}
    response = u.post(data=j, headers=headers)
    response['identifier'] = news_preprocessed.identifier
    return Media_DataModel(**response)

def topics_getter(news_preprocessed:News_DataModel):
    u = URLRequest(url_service_media+"/api/extract_topics")
    payload = {"articleBody": news_preprocessed.articleBody,
               "headline": news_preprocessed.headline,
               "identifier": news_preprocessed.identifier,
               "language" : "language" }#####---->modify when ready from upm preprocessing 
    j = json.dumps(payload)
    headers = {'content-type': "application/json",'accept': "application/json"}
    response = u.post(data=j, headers=headers)
    return Topics_DataModel(**response)


def similar_claims(claim_input: Claim_input) -> list:
    u = URLRequest(url_similar_claims+"/fandango/v0.1/siren/findSimilarClaims")
    payload = {"identifier":"","text": claim_input.text, "topics" : []}
    headers = {"Content-Type":  "application/json"}
    j = json.dumps(payload)
    response = u.post(data=j,headers = headers)
   
    for i in response['results']: 
        print(i)
    opendata = Open_Data(text=claim_input.text, category=claim_input.text, topics= claim_input.topics)
    op = get_opendata(opendata)
    result = {"similar_claim":response['results'], "open_data": op }
    print(result)
    return result


def similar_news(id_news:str) -> list:
    print("start similar news")
    u = URLRequest(url_similar_claims+"/fandango/v0.1/siren/FindSimilarArticles")
    payload = {"identifier": id_news}
    headers = {"Content-Type":  "application/json"}
    
    j = json.dumps(payload)
    response = u.post(data=j,headers = headers)
    for i in response['results']: 
        if i['sourceDomain']=='www.repubblica.it':
            i["calculatedRatingDetail"]["textRating"]=1.0
    return response["results"]



#------------------------------------>App FLASK <----------------------------------


app=DS4BizFlask(__name__,static_folder=static_folder+"/dist/",static_url_path="",template_folder='../templates/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html')

app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
#app.add_service("crawl_online", crawl_online, method= 'POST')
#app.add_service("preprocessing_online", preprocessing_online, method = 'POST')
app.add_service("crawl_and_preprocessing",crawl_prep, method = 'GET')
#app.add_service("author_and_organizations",author_org_getter, method = 'POST')
#app.add_service("Medias", media_getter, method = 'POST')
#app.add_service("topics and entities",topics_getter , method = 'POST' )
#app.add_service("aggregator", finalaggr, method= 'POST')
app.add_service("get_opendata", get_opendata, method= 'POST')
app.add_service("get_languages",get_languages, method = 'GET')
app.add_service("analyzer",analyzer, method='POST')
app.add_service("feedback",feedback, method='POST')
app.add_service("start_daemon",start_daemon, method='POST')
app.add_service("info_score",info_score, method = 'GET')
app.add_service("ping_image",ping_image, method = 'GET')
app.add_service("ping_video",ping_video, method = 'GET')
app.add_service("similar_claims",similar_claims, method = 'POST')
app.add_service("url_image_score",url_image_score, method = 'GET')
app.add_service("url_video_score",url_video_score, method = 'GET')
app.add_service("similar_news",similar_news, method = 'POST')
app.add_service("upload_image",upload_image, method = 'POST')


CORS(app)
    
log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT))
app.setup()
app.run(host = "0.0.0.0", port = AppConfig.BASEPORT,debug=False)

#===============================================================================
# 
# def analyzer(daopredictor,nome_modello,news_preprocessed:News_DataModel) ->  str:
#     
#     
#     log.info('''ANALISI NEWS''')
#     model = daopredictor.get_by_id(nome_modello)
#     df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
#     print(df.columns)
#     prest = model.predict_proba(df)
#     prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
#     log.info(json.loads(prest.to_json(orient='records')))
#     result = json.loads(prest.to_json(orient='records'))
#     
#     return str(result[0]['REAL'])
#===============================================================================

# def finalaggr(news_preprocessed:News_DataModel)-> str:
#     
#     d = {"headline": news_preprocessed.headline,
#             "articleBody" : news_preprocessed.articleBody,
#                "dateCreated": news_preprocessed.dateCreated,
#                "dateModified": news_preprocessed.dateModified,
#                "datePublished": news_preprocessed.datePublished,
#                "author": news_preprocessed.author,
#                "publisher": news_preprocessed.publisher,
#                "sourceDomain": news_preprocessed.sourceDomain,
#                "calculatedRatingDetail": news_preprocessed.calculateRatingDetail,
#                "calculatedRating": analyzer(news_preprocessed)[0]['REAL'],
#                "identifier": news_preprocessed.identifier}
#     
#     
#     d['author'] = author_org_getter(news_preprocessed).author
#     d['publisher'] = author_org_getter(news_preprocessed).publisher
#     d['images'] = media_getter(news_preprocessed).images
#     d['videos'] = media_getter(news_preprocessed).videos
#     d['mentions'] = topics_getter(news_preprocessed).mentions
#     d['about'] = topics_getter(news_preprocessed).about
#     dao.create_doc_news(d)
#     #print(d, Final_DataModel(**d))
#===============================================================================

#===============================================================================
# def author_org_getter(news_preprocessed:News_DataModel) -> Author_org_DataModel:
#     
#     payload = {"headline": news_preprocessed.headline,
#                "articleBody" : news_preprocessed.articleBody,
#                "dateCreated": news_preprocessed.dateCreated,
#                "dateModified": news_preprocessed.dateModified,
#                "datePublished": news_preprocessed.datePublished,
#                "author": news_preprocessed.author,
#                "publisher": news_preprocessed.publisher,
#                "images": news_preprocessed.images,
#                "video": news_preprocessed.video,
#                "sourceDomain": news_preprocessed.sourceDomain,
#                "calculateRatingDetail": news_preprocessed.calculateRatingDetail,
#                "calculateRating": -news_preprocessed.calculateRating,
#                "identifier": news_preprocessed.identifier}
# 
#     u = URLRequest(url_service_upm+"/graph/article")
#     
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     return Author_org_DataModel(**response)
# 
# 
# def media_getter(news_preprocessed:News_DataModel) -> Media_DataModel :
#     
#     u = URLRequest(url_service_certh+"/api/media_analysis")
#     payload = {"images": news_preprocessed.images,"videos": news_preprocessed.videos,"identifier": news_preprocessed.identifier}
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     response['identifier'] = news_preprocessed.identifier
#     return Media_DataModel(**response)
# 
# def topics_getter(news_preprocessed:News_DataModel) -> Topics_DataModel:
#     u = URLRequest(url_service_certh+"/api/extract_topics")
#     payload = {"articleBody": news_preprocessed.articleBody,
#                "headline": news_preprocessed.headline,
#                "identifier": news_preprocessed.identifier,
#                "language" : "language" }#####---->modify when ready from upm preprocessing 
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     return Topics_DataModel(**response)
#===============================================================================
#===============================================================================
# 
# def finalaggr(news_preprocessed:News_DataModel)-> str:
#     
#     d = {"headline": news_preprocessed.headline,
#             "articleBody" : news_preprocessed.articleBody,
#                "dateCreated": news_preprocessed.dateCreated,
#                "dateModified": news_preprocessed.dateModified,
#                "datePublished": news_preprocessed.datePublished,
#                "author": news_preprocessed.author,
#                "publisher": news_preprocessed.publisher,
#                "sourceDomain": news_preprocessed.sourceDomain,
#                "calculatedRatingDetail": news_preprocessed.calculateRatingDetail,
#                "calculatedRating": analyzer(news_preprocessed)[0]['REAL'],
#                "identifier": news_preprocessed.identifier}
#     
#     
#     d['author'] = author_org_getter(news_preprocessed).author
#     d['publisher'] = author_org_getter(news_preprocessed).publisher
#     d['images'] = media_getter(news_preprocessed).images
#     d['videos'] = media_getter(news_preprocessed).videos
#     d['mentions'] = topics_getter(news_preprocessed).mentions
#     d['about'] = topics_getter(news_preprocessed).about
#     dao.create_doc_news(d)
#     #print(d, Final_DataModel(**d))
# 
#     return('ciao')
#===============================================================================



