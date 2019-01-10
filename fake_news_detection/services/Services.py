'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizFlask import DS4BizFlask
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel, \
    InterfaceInputFeedBack, News, News_annotated, News_domain,\
    New_news_annotated
from fake_news_detection.dao.PickleDao import ModelDao
from fake_news_detection.business.Model import SklearnModel
from flask_cors.extension import CORS
import json
from fake_news_detection.config import AppConfig
from fake_news_detection.config.AppConfig import static_folder
from fake_news_detection.utils.Crawler import crawler_news
from flask import request
from fake_news_detection.business.IndexLiar import IndexLiar, popolate
from ds4biz_flask.model.DS4BizTyping import DS4BizList
from fake_news_detection.model.Language import Language
from fake_news_detection.business import getAnnotated
from fake_news_detection.dao.DAO import DAONewsElastic
 
oo = ModelDao()
dao_news = DAONewsElastic()
 
model = oo.load('test')
    
    
def feedback(info:InterfaceInputFeedBack) -> str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    text = info.text.replace("\n", " ")
    model.partial_fit(info.title, text, info.label)
    return "OK"


def get_languages() -> DS4BizList(Language):
    l = list()
    l.append(Language("en", "English", True))
    l.append(Language("it", "Italian", True))
    l.append(Language("es", "Spanish", False))
    l.append(Language("pt", "Portuguese", True))
    l.append(Language("el_GR", "Greek", False))
    return l

    
def next_news(lang:str) -> News:
    print(lang)
    try:
        news = dao_news.next(languages=lang)
    except StopIteration:
        return {"END":"True",
            "title":"ALL NEWS ANNOTATED"}
    return news
 # News('news1','www.thegurdian.uk','sono il titolo', 'ciao, sono il testo','sono lautore', 'sono lente')    

    
def new_annotation(annotation:News_annotated) -> str:
    
    print('id:' , annotation.id, 'label:', annotation.label)
    dao_news.set_label(annotation.id, annotation.label)
    return 'DONE'


    


def domain_annotation(list_u:News_domain) -> str:
    
    print([i for i in list_u.list_url.strip().split("\n")])
    
    return( "DONE")


def new_doc_annotation(new_record:New_news_annotated)->str:
    news_crawled = crawler_news(new_record.url)
    news_crawled['label'] = new_record.label
    news_crawled['language'] = new_record.lang
    
    dao_news.create_doc_news(news_crawled)
    print(news_crawled)
    return('DONE')
  
        
    

# TODO
# ATTIVARE NEW DOCUMENT
# pisu invierà il documento paripari a come gli da crawler e aggiungerà la lingua
# e la label
# va dirottato in  create_doc_news


    
def analyzer(info:InterfaceInputModel) -> str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    print(info.title, info.text)
    text = info.text.replace("\n", " ")
    prest = model.predict(info.title, text)
    print(json.loads(prest.to_json(orient='records')))
    
    return json.loads(prest.to_json(orient='records'))


def crawler(url:str) -> str:
    print(url)
    return crawler_news(url)


def claim(text:str) -> str:
    j = request.get_json()  # key txt of the dictionary
    text = j.get("text")
    I = IndexLiar()
    j_resp = I.similarClaims(text, max_claims=5)
    return j_resp


def popolate_claims() -> str: 
    popolate()
    return "DONE"



    
    
app = DS4BizFlask(__name__, static_folder=static_folder + "/dist/", static_url_path="/web")
app.root = "/fandango/v0.3/fakeness"
app.name = "FANDANGO"
app.add_service("analyzer", analyzer, method='POST')
app.add_service("cr_url", crawler, method='POST')
app.add_service("feedback", feedback, method='POST')
app.add_service("claim", claim, method='POST')
app.add_service("popolate_claims", popolate_claims, method='GET')
app.add_service("get_languages", get_languages, method='GET')
app.add_service("next_news", next_news, method='POST')
app.add_service("new_annotation", new_annotation, method='POST')
app.add_service('domain_annotation', domain_annotation, method='POST')
app.add_service('new_document_annotation', new_doc_annotation, method = 'POST') 
CORS(app)

print("RUN ON ", AppConfig.BASEURL, AppConfig.BASEPORT)
app.run(host="0.0.0.0", port=AppConfig.BASEPORT, debug=False)


