'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizFlask import DS4BizFlask

from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel, \
    InterfaceInputFeedBack, News, News_annotated, News_domain,\
    New_news_annotated, Claims_annotated
from flask_cors.extension import CORS
import json
from fake_news_detection.config import AppConfig
from fake_news_detection.config.AppConfig import static_folder, picklepath
from fake_news_detection.utils.Crawler import crawler_news
from flask import request
import pandas as pd
from ds4biz_flask.model.DS4BizTyping import DS4BizList
from fake_news_detection.model.Language import Language

from fake_news_detection.dao.DAO import DAONewsElastic, FSMemoryPredictorDAO
from fake_news_detection.business.ClaimsManager import popola_all
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.dao.ClaimDAO import DAOClaimsOutputElastic,\
    DAOClaimsOutput
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD,\
    DAOTrainingElasticByDomains
from typing import List
 
###oo = ModelDAO()

daopredictor = FSMemoryPredictorDAO(picklepath)
daotrainingset = DAOTrainingPD()

dao_news=DAONewsElastic()
#dao_news=DAONews()
#dao_claim_output=DAOClaimsOutput()
dao_claim_output=DAOClaimsOutputElastic()
log = getLogger(__name__)
 
###model = oo.load('test')
nome_modello="modello_en_3"


def train_model() -> str:
    #training_set = daotrainingset.get_train_dataset(sample_size=0.01)
    train_config=train_model()
    dao_train = DAOTrainingElasticByDomains()
    #training_set = train_config.load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.1)
    training_set=dao_train.get_train_dataset()
    training_set_final = train_config.preprocess_df(training_set)
    train_config.training(nome_modello, training_set_final, daopredictor)


def feedback(info:InterfaceInputFeedBack) -> str:
    log.debug(info)
    model=daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n", " ")]})
    train_config=train_model()
    training_set_final = train_config.rapreprocess_df(df)
    model.partial_fit(training_set_final, pd.Series(info.label))
    daopredictor.update(model)
    return "OK"


def get_languages() -> DS4BizList(Language):
    l= list()
    l.append(Language("en","English",True))
    l.append(Language("it","Italian",True))
    l.append(Language("es","Spanish",False))
    l.append(Language("pt","Portuguese",True))
    l.append(Language("el_GR","Greek",False))
    return l


def next_news(lang:str) -> News:
    log.debug(lang)
    try:
        news=dao_news.next(languages=lang)
    except StopIteration:
        return {"END":"True",
            "title":"ALL NEWS ANNOTATED"}
    return news
 # News('news1','www.thegurdian.uk','sono il titolo', 'ciao, sono il testo','sono lautore', 'sono lente')

    
def new_annotation(annotation:News_annotated) -> str:
    log.debug('id: {id}, label: {lbl}'.format(id= annotation.id, lbl=annotation.label))
    annotation.label = "A#"+annotation.label
    dao_news.set_label(annotation.id, annotation.label)
    return 'DONE'


def domain_annotation(list_u:News_domain) -> str:
    dao_news.create_source(list_u)
    log.debug("New domain source to annotate reiceived :{sou}".format(sou=list_u))  
    return( "DONE")


def new_doc_annotation(new_record:New_news_annotated) -> str:
    news_crawled = crawler_news(new_record.url)
    new_record.label ="M#"+new_record.label
    news_crawled['label'] = new_record.label
    news_crawled['language'] = new_record.lang
    dao_news.create_doc_news(news_crawled)
    log.debug(news_crawled)
    return('DONE')


def analyzer(info:InterfaceInputModel) -> str:
    log.info('''ANALISI NEWS''')
    model = daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n"," ")]})
    train_config = train_model()
    df_new = train_config.preprocess_df(df)
    prest = model.predict_proba(df_new)
    prest = pd.DataFrame(prest, columns=model.predictor.predictor.classes_)
    log.info(json.loads(prest.to_json(orient='records')))
    return json.loads(prest.to_json(orient='records'))


def new_claim_annotated(new_claim: Claims_annotated) -> str:
    if dao_claim_output.check_claim_existence(new_claim.claim):
        new_record = {"claim" : new_claim.claim, "label": new_claim.label}
        dao_claim_output.add_claim(new_record)
        return('new claim added')
    else:
        return('claim already in database')


def crawler(url:str) -> str:
    log.debug(url)
    return crawler_news(url)


def claim() -> str:
    j = request.get_json()  #key txt of the dictionary
    text = j.get("text")
    j_resp =dao_claim_output.get_similarity_claims_from_text(text)
    return j_resp
    #===========================================================================
    # print(text)
    # res = dao_claim_output.get_similarity_claims_from_text(text)
    # print(res)
    # return(res)
    #===========================================================================


def popolate_claims() -> str:
    popola_all(dao_claim_output)
    return "DONE"

    
    
app=DS4BizFlask(__name__,static_folder=static_folder+"/dist/",static_url_path="/web")
app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
app.add_service("train",train_model, method='POST')
app.add_service("analyzer",analyzer, method='POST')
app.add_service("cr_url",crawler, method='POST')
app.add_service("feedback",feedback, method='POST')
app.add_service("claim", claim, method = 'POST')
app.add_service("popolate_claims", popolate_claims, method = 'GET')
app.add_service("get_languages",get_languages, method = 'GET')
app.add_service("next_news", next_news, method ='POST')
app.add_service("new_annotation", new_annotation, method = 'POST')
app.add_service("new_doc_annotation", new_doc_annotation, method = 'POST')
app.add_service('domain_annotation', domain_annotation, method = 'POST')
app.add_service('new_claim_annotated', new_claim_annotated, method = 'POST')
CORS(app)


log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT))
app.run(host="0.0.0.0", port=AppConfig.BASEPORT,debug=False)
