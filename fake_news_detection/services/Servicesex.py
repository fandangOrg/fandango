'''
Created on 10 apr 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import News_DataModel,\
    News_raw, Topics_DataModel, Videos_DataModel, Images_DataModel,\
    Author_org_DataModel
from ds4biz_flask.model.ds4bizflask import DS4BizFlask
from fake_news_detection.config.AppConfig import static_folder, url_service_upm
from flask_cors.extension import CORS
from fake_news_detection.config import AppConfig
from fake_news_detection.utils.logger import getLogger
import requests
import ds4biz_commons
from ds4biz_commons.utils.requests_utils import URLRequest
import json
from typing import Dict

log = getLogger(__name__)



##########################ONLINE SERVICES TEST####################################

def crawl_online(url:str) -> News_raw: 
    
    log.debug(url)
    print(url)
    data = News_raw(**{
            "description" : "Lorem fistrum esse por la gloria",
            "title": "Lorem fistrum esse por la gloria",
            "fakeness": "bias",
            "text":"Lorem fistrum esse por la gloria",
            "texthash" : "453218461353464615",
            "images": ["URL"],
            "top_image":"URL",
            "url": url,
            "version" : "example version",
            "videos": ["URL","URL"],
            "date_created": "",
            "date_modified": "2018-01-23T09:10:12.451Z",
            "date_published": "2018-01-23T09:05:12.451Z",
            "authors": ["NAME1","NAME2","NAM3"],
            "language": "en",
            "source_domain": "www.ccn.com",
            "keywords": ["WORD3", "WORD34"],
            "summary" : "Lorem fistrum esse por la gloria"})
    return data


#===============================================================================
# def preprocessing_online2(raw_news:News_raw) -> str:
#     url = "http://138.4.47.33:5006/preprocess/article"
#     
#     payload = "\"{\"fakeness\": \""+raw_news.fakeness+"\",\"source_domain\": \""+raw_news.source_domain+"\",\"description\": \""+raw_news.description+"\",\"videos\":"+str(raw_news.videos)+",\"title\": \""+raw_news.title+"\",\"language\": \""+ raw_news.language+",\"text\": \""+raw_news.text+"\",\"date_modified\": \""+raw_news.date_modified+"\",\"spider\": \""+raw_news.spider+"\",\"summary\": \""+raw_news.summary+"\",\"url\": \""+raw_news.url+"\",\"keywords\":"+str(raw_news.keywords)+",\"authors\":"+ str(raw_news.authors)+",\"images\":"+str(raw_news.images)+",\"date_created\": \""+raw_news.date_created+"\",\"top_image\": \""+ raw_news.top_image+"\",\"texthash\": \""+raw_news.texthash+"\"}\""
#     #payload = "{\"fakeness\": \""+raw_news.fakeness+"\",\"source_domain\": \""+raw_news.source_domain+"\",\"description\": \""+raw_news.description+"\",\"videos\": "+str(raw_news.videos)+",\"title\": \""+raw_news.title+"\",\"language\": \""+ raw_news.language+"\",\"text\": \""+raw_news.text+"\",\"date_modified\": \""+raw_news.date_modified+"\",\"spider\": \""+raw_news.spider+"\",\"summary\": \""+raw_news.summary+"\",\"url\": \""+raw_news.url+"\",\"keywords\": [\"Lorem\",\"ipsum\"],\"authors\": [\"\",\"Mark Prigg For Dailymail.com\"],\"images\": [\"https://i.dailymail.co.uk/1s/2018/11/09/12/5979502-0-image-a-16_1541765781497.jpg\",\"https://i.dailymail.co.uk/1s/2018/11/09/17/5989332-0-image-a-13_1541782973758.jpg\"],\"date_created\": \"2019-03-16 15:07:26\",\"top_image\": \"https://i.dailymail.co.uk/1s/2018/11/09/17/5989332-0-image-a-13_1541782973758.jpg\",\"texthash\": \"05353d6f40168e069ea3636ba8e1798f\"}"
#     print(payload)
#     #payload = "{\"fakeness\": \"bad\",\"source_domain\": \"www.dailymail.co.uk\",\"description\": \"Lorem ipsum dolor sit amet\",\"videos\": [\"https://www.youtube.com/v/null&hl=en&fs=1&rel=0&color1=0x3a3a3a&color2=0x999999\"],\"title\": \"Joanna Yeates murder: Landlord Chris Jefferies could hold key?\",\"language\": \"en\",\"text\": \"Could landlord hold the key to Joanna's murder? 'I saw her leave with two others and talking in hushed tones' In custody: Chris Jefferies, the landlord of Joanna Yeates, pictured yesterday. The landlord of murdered architect Jo Yeates watched as she left her flat with two people on the night she disappeared, it was claimed yesterday. ... I have full confidence in the police, father insists. The father of Jo Yeates yesterday backed the way police are conducting their inquiry, adding he feels sure they will catch her killer. David Yeates, 63, said he had complete faith in the investigation into his daughter’s death.  At his £600,000 home in Ampfield, Hampshire, he said: ‘The police have been really helpful in this investigation and we have every faith in them. ‘We all want to find whoever is responsible for Jo’s death.’\",\"date_modified\": \"2019-03-16 15:07:26\",\"spider\": \"english\",\"summary\": \"Lorem ipsum dolor sit amet\",\"url\": \"https://www.dailymail.co.uk/news/Joanna-Yeates-murder-Landlord-Chris-Jefferies-hold-key.html\",\"keywords\": [\"Lorem\",\"ipsum\"],\"authors\": [\"\",\"Mark Prigg For Dailymail.com\"],\"images\": [\"https://i.dailymail.co.uk/1s/2018/11/09/12/5979502-0-image-a-16_1541765781497.jpg\",\"https://i.dailymail.co.uk/1s/2018/11/09/17/5989332-0-image-a-13_1541782973758.jpg\"],\"date_created\": \"2019-03-16 15:07:26\",\"top_image\": \"https://i.dailymail.co.uk/1s/2018/11/09/17/5989332-0-image-a-13_1541782973758.jpg\",\"texthash\": \"05353d6f40168e069ea3636ba8e1798f\"}"
# 
#     headers = {
#     'content-type': "application/json",
#     'accept': "application/json",
#     'cache-control': "no-cache",
#     'postman-token': "a8c09a34-e153-27f6-59a7-9686c33a7234"
#     }
# 
#     response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
#     return str(response.text)
#===============================================================================

def preprocessing_online2(raw_news:News_raw) -> News_DataModel:
    
    ip = "http://138.4.47.33"
    port = "5006"
    
    u = URLRequest(ip+":"+port+"/preprocess/article")
    payload = {"fakeness": raw_news.fakeness,
               "source_domain": raw_news.source_domain,
               "description": raw_news.description,
               "videos":raw_news.videos,
               "title": raw_news.title,
               "language": raw_news.language,
               "text": raw_news.text,
               "date_modified": raw_news.date_modified,
               "spider": raw_news.spider,
               "summary": raw_news.summary,
               "url": raw_news.url,
               "keywords": raw_news.keywords,
               "authors": raw_news.authors,
               "images": raw_news.images,
               "date_created": raw_news.date_created,
               "top_image": raw_news.top_image,
               "texthash": raw_news.texthash
               }
    
    print(payload)
    j = json.dumps(payload)
    headers = {
        'content-type': "application/json",
        'accept': "application/json"
    }

    response = u.post(data=j, headers=headers)
    data_prep = News_DataModel(**response)
    return data_prep


#===============================================================================
#     
# def preprocessing_online(raw_news:News_raw) -> News_DataModel:
#     data = News_DataModel(**{
#                 "headline": "headline1",
#                 "articleBody":"Lorem fistrum esse por la gloria",
#                 "images": ["URL"],
#                 "video": ["URL","URL"],
#                 "dateCreated": "",
#                 "dateModified": "2018-01-23T09:10:12.451Z",
#                 "datePublished": "2018-01-23T09:05:12.451Z",
#                 "author": ["NAME1","NAME2","NAM3"],
#                 "publisher": ["ORG1","ORG2"],
#                 "sourceDomain": "www.ccn.com",
#                 "calculateRatingDetail": "",
#                 "calculateRating": -99})
# 
#     return data
#===============================================================================


def author_org_scores(news_preprocessed:News_DataModel) -> Author_org_DataModel:
    
    
    u = URLRequest(url_service_upm+"/graph/article")
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

    j = json.dumps(payload)
    headers = {'content-type': "application/json",'accept': "application/json"}

    response = u.post(data=j, headers=headers)
    return Author_org_DataModel(**response)


    
def images_scores(news_preprocessed:News_DataModel) -> Images_DataModel :
    
    u = URLRequest(url_service_upm+"/graph/article")
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

    j = json.dumps(payload)
    headers = {'content-type': "application/json",'accept': "application/json"}

    response = u.post(data=j, headers=headers)
    return Author_org_DataModel(**response)
    
    data = Images_DataModel(**{ "identifier":"0001", "images" : ["5a66fac854ad4acb3528e380"] })
    return data
def video_scores(news_preprocessed:News_DataModel) -> Videos_DataModel:
    data = Videos_DataModel(**{ "identifier":"0001", "videos" : ["5a66fac854ad4acb3528e380"] })
    return data

def ner(news_preprocessed:News_DataModel) -> Topics_DataModel:
    data = Topics_DataModel(**{"identifier": "0001","contains": ["5a66fac854ad4acb3528e382","5a66fac854ad4acb3528e383"],
            "mentions": ["5a66fac854ad4acb3528e39a", "5a66fac854ad4acb3528e39c"]})
    return data


app=DS4BizFlask(__name__,static_folder=static_folder+"/dist/",static_url_path="/web")
app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
app.add_service("crawler_online", crawl_online, method= 'POST')
#app.add_service("preprocessing_online", preprocessing_online, method = 'POST')
app.add_service("author_organization",author_org_scores, method='POST')
app.add_service("images_scores", images_scores, method = 'POST') 
app.add_service("video_scores", video_scores, method = 'POST')
app.add_service("ner", ner, method = 'POST')
app.add_service("preprocessing_online2",preprocessing_online2, method = 'POST')
CORS(app)

log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT))
app.setup()
app.run(host = "0.0.0.0", port = AppConfig.BASEPORT,debug=False)


