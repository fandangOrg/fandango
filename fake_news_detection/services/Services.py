'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizFlask import DS4BizFlask
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel,\
    InterfaceInputFeedBack, News, News_annotated, News_domain
from fake_news_detection.dao.PickleDAO import ModelDAO
from flask_cors.extension import CORS
import json
from fake_news_detection.config import AppConfig
from fake_news_detection.config.AppConfig import static_folder
from fake_news_detection.utils.Crawler import crawler_news
from flask import request
from ds4biz_flask.model.DS4BizTyping import DS4BizList
from fake_news_detection.model.Language import Language
from fake_news_detection.dao.DAO import DAONewsElastic
from fake_news_detection.business.ClaimsManager import popola_all, similar_claims
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.dao.ClaimDAO import DAOClaimsOutputElastic
 
oo = ModelDAO()
dao_news=DAONewsElastic()
dao_claim_output=DAOClaimsOutputElastic()
log = getLogger(__name__)
 
model = oo.load('test')
    
    
def feedback(info:InterfaceInputFeedBack)->str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    text=info.text.replace("\n"," ")
    model.partial_fit(info.title,text,info.label)
    return "OK"

def get_languages()->DS4BizList(Language):
    l= list()
    l.append(Language("en","English",True))
    l.append(Language("it","Italian",True))
    l.append(Language("es","Spanish",False))
    l.append(Language("pt","Portuguese",True))
    l.append(Language("el_GR","Greek",False))
    return l
    
def next_news(lang:str)->News:
    try:
        news=dao_news.next(languages=lang)
    except StopIteration:
        return {"END":"True",
            "title":"ALL NEWS ANNOTATED"}
    return news
 # News('news1','www.thegurdian.uk','sono il titolo', 'ciao, sono il testo','sono lautore', 'sono lente')    
    
def new_annotation(annotation:News_annotated)-> str:
    dao_news.set_label(annotation.id, annotation.label)
    return 'DONE'

def domain_annotation(list_url:News_domain)->str:
    list_url = list_url.domain.split('\n')
    print(i.domain for i in list_url) 
    return 'DONE'
    
    
#TODO
#ATTIVARE NEW DOCUMENT
#pisu invierà il documento paripari a come gli da crawler e aggiungerà la lingua
#e la label
#va dirottato in  create_doc_news
    
    
def analyzer(info:InterfaceInputModel)->str:
    log.info(info)
    log.info('''Creazione di un nuovo analizzatore per i social''')
    log.info(info.title,info.text)
    text=info.text.replace("\n"," ")
    prest=model.predict(info.title,text)
    log.info(json.loads(prest.to_json(orient='records')))
    
    return json.loads(prest.to_json(orient='records'))

def crawler(url:str)->str:
    print(url)
    return crawler_news(url)

def claim(text:str)->str:
    j = request.get_json()  #key txt of the dictionary
    text = j.get("text")
    j_resp =similar_claims(dao_claim_output,text)
    return j_resp

def popolate_claims()->str: 
    popola_all(dao_claim_output)
    return "DONE"
    
    
app=DS4BizFlask(__name__,static_folder=static_folder+"/dist/",static_url_path="/web")
app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
app.add_service("analyzer",analyzer, method='POST')
app.add_service("cr_url",crawler, method='POST')
app.add_service("feedback",feedback, method='POST')
app.add_service("claim", claim, method = 'POST')
app.add_service("popolate_claims", popolate_claims, method = 'GET')
app.add_service("get_languages",get_languages, method = 'GET')
app.add_service("next_news", next_news, method ='POST')
app.add_service("new_annotation", new_annotation, method = 'POST')
app.add_service('domain_annotation', domain_annotation, method = 'POST')
CORS(app)


log.info("RUN ON ",AppConfig.BASEURL,AppConfig.BASEPORT)
app.run(host="0.0.0.0", port=AppConfig.BASEPORT,debug=False)
