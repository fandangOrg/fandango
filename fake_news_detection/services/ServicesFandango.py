'''
Created on 23 apr 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import News_DataModel, Author_org_DataModel, Media_DataModel, Topics_DataModel,\
 InterfaceInputFeedBack, Claim_input, Claim_output
from ds4biz_commons.utils.requests_utils import URLRequest
from fake_news_detection.config.AppConfig import  static_folder, url_service_media,\
    url_service_authors, url_similar_claims, template_path
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
#from fake_news_detection.apps.daemon import daemon_run


log = getLogger(__name__)
service_scrapy=ScrapyService()
service_analyzer=AnalyticsService()
###run deamon

daemon_run()

headers = {'content-type': "application/json",'accept': "application/json"}

def info_score(label:str) -> str:     
    return LABEL_SCORE.get(label)

def start_daemon() -> str:
    daemon_run()
    return "done"

def analyzer(news_preprocessed:News_DataModel) -> str:
    log.info('''ANALISI NEWS'''+str(news_preprocessed.sourceDomain))
    prest=service_analyzer.analyzer(news_preprocessed)
#===============================================================================
# =======
#     log.info('''ANALISI NEWS''')
#     model = daopredictor.get_by_id(nomhttp://www.ansa.it/robots.txte_modello)
#     df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
#     
#     prest = model.predict_proba(df)
#     prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
# >>>>>>> develop-0.4
#===============================================================================    
    print(prest)
    #log.info(json.loads(prest))
    return prest
    #===========================================================================
    # log.info(json.loads(prest.to_json(orient='records')))
    # return json.loads(prest.to_json(orient='records'))
    #===========================================================================


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



def get_languages() -> List[Language]:
    l= list()
    l.append(Language("en","English","True"))
    l.append(Language("it","Italian","True"))
    l.append(Language("es","Spanish","True"))
    return l

def feedback(info:InterfaceInputFeedBack) -> str:
    log.info(info)
    #===========================================================================
    # model=daopredictor.get_by_id(nome_modello)
    # df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n", " ")],'label': [info.label.replace("\n", " ")]})
    # model.partial_fit(df)
    # daopredictor.update(model)
    #===========================================================================
    return "OK"


#def crawl_online(url:str) -> News_raw: 
    
    
    
#===============================================================================
# def preprocessing_online(raw_news:News_raw) -> News_DataModel:
#     
#     payload = raw_news.__dict__
#     payload["fakeness" ]= ""
#     #===========================================================================
#     # payload = {"fakeness" : "",
#     #            "source_domain": raw_news.source_domain,
#     #            "description": raw_news.description,
#     #            "videos":raw_news.videos,
#     #            "title": raw_news.title,
#     #            "language": raw_news.language,
#     #            "text": raw_news.text,
#     #            "date_modified": raw_news.date_modified,
#     #            "spider": raw_news.spider,
#     #            "summary": raw_news.summary,
#     #            "url": raw_news.url,
#     #            "keywords": raw_news.keywords,
#     #            "authors": raw_news.authors,
#     #            "images": raw_news.images,
#     #            "date_created": raw_news.date_created,
#     #            "top_image": raw_news.top_image,
#     #            "texthash": raw_news.texthash
#     #            }
#     #===========================================================================
#      
#     u = URLRequest(url_service_upm+"/preprocess/article")
#     j = json.dumps(payload)
#     response = u.post(data=j, headers=headers)
#     print(response)
#     return News_DataModel(**response)
#===============================================================================
def crawl_prep(url:str) -> News_DataModel:
    news_preprocessed= service_scrapy.scrapy(url)
    print(news_preprocessed.__dict__)
    prest=service_analyzer.analyzer(news_preprocessed)
    news_preprocessed.results=prest
    return news_preprocessed
#===============================================================================

def ping_image(id:str) -> News_DataModel:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/analyze_image/"+id)
    return u.get(headers=headers)

def ping_video(id:str) -> str:
    headers = {'content-type': "application/json",'accept': "application/json"}
    u = URLRequest(url_service_media+"/api/analyze_video/"+id)
    return u.get(headers=headers)
      
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
    print("RICHIESTA IMMAGINI  ",payload)
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
    print(response)
    list_claims = []
    for i in response['results']: 
        for j in i['claimReviews']:
            list_claims.append({"text" : i['text'], "datePublished":i['datePublished'], "reviewBody":j['reviewBody']})
    
    return list_claims
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





    
    
    
    
    
#------------------------------------>DECODING ELASTIC ID SERVICES<----------------------------------

app=DS4BizFlask(__name__,static_folder=static_folder+"/dist/",static_url_path="",template_folder='../templates/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html')


app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
#app.add_service("crawl_online", crawl_online, method= 'POST')
#app.add_service("preprocessing_online", preprocessing_online, method = 'POST')
app.add_service("crawl_and_preprocessing",crawl_prep, method = 'POST')
#app.add_service("author_and_organizations",author_org_getter, method = 'POST')
#app.add_service("Medias", media_getter, method = 'POST')
#app.add_service("topics and entities",topics_getter , method = 'POST' )
#app.add_service("aggregator", finalaggr, method= 'POST')
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

CORS(app)

log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT))
app.setup()
app.run(host = "0.0.0.0", port = AppConfig.BASEPORT,debug=False)





