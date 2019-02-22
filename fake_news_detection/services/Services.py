'''
Created on Oct 18, 2018

@author: daniele
'''

from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel, \
    InterfaceInputFeedBack, News, News_annotated, News_domain,\
    New_news_annotated, Claims_annotated, Prestazioni, Info
from flask_cors.extension import CORS
import json
from flask import json
from fake_news_detection.config import AppConfig
from fake_news_detection.config.AppConfig import static_folder, picklepath,\
    number_item_to_train
from fake_news_detection.utils.Crawler import crawler_news
from flask import request
import pandas as pd

from fake_news_detection.dao.DAO import DAONewsElastic, FSMemoryPredictorDAO
from fake_news_detection.business.ClaimsManager import popola_all
from fake_news_detection.utils.logger import getLogger
from fake_news_detection.dao.ClaimDAO import DAOClaimsOutputElastic,\
    DAOClaimsOutput
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains
from typing import List
from fake_news_detection.model.predictor import Preprocessing, FakePredictor
from fake_news_detection.config.MLprocessConfig import config_factory
from ds4biz_flask.model.ds4bizflask import DS4BizFlask
from fake_news_detection.model.Language import Language
from fake_news_detection.dao.AuthorDAO import DAOAuthorOutputElastic
import ast
 
###oo = ModelDAO()

#daotrainingset = DAOTrainingPD()

#dao_news=DAONews()
#dao_claim_output=DAOClaimsOutput()
daopredictor = FSMemoryPredictorDAO(picklepath)
dao_news=DAONewsElastic()
dao_claim_output=DAOClaimsOutputElastic()
log = getLogger(__name__)
dao_authors = DAOAuthorOutputElastic()
###model = oo.load('test')
nome_modello="english_first_version"
logger = getLogger(__name__) 



#-----------------> MODEL SERVICES--------------------------------------------------------------
def train_model_old() -> str:
    #training_set = daotrainingset.get_train_dataset(sample_size=0.01)
    train_config=None#Train_model()
    list_domains = dao_news.get_domain()
    dao_train = DAOTrainingElasticByDomains(list_domains)
    #training_set = train_config.load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.1)
    training_set=dao_train.get_train_dataset()
    training_set_final = train_config.preprocess_df(training_set)
    train_config.training(nome_modello, training_set_final, daopredictor)

def train_model()->Prestazioni:

    '''training a classification model'''
    modello = None
    try:
        modello = daopredictor.get_by_id(nome_modello)
    except:
        pass

    if modello:
        return "MODELLO GIÀ ESISTE"
        #raise CustomHttpException(*ALREADY_EXIST(info.nome_modello))

    #try:
    preprocessing = Preprocessing("en")
    #except Exception as e:
    #    logger.error(e)
    #    raise CustomHttpException(*LANGUAGE_ERROR())

    #===========================================================================
    # try:
    #===========================================================================
    logger.info("creazione modello "+nome_modello)
    predictor_fakeness = config_factory.create_model_by_configuration("fandango","1","english")
    predictor=FakePredictor(predictor_fakeness,preprocessing,nome_modello,'fakeness')
    list_domains = dao_news.get_domain()
    dao_train = DAOTrainingElasticByDomains(list_domains)
    #training_set = train_config.load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.1)
    training_set=dao_train.get_train_dataset(limit=number_item_to_train)
    #training_set.to_csv( '/home/daniele/resources/greenl.csv',index=False)
    predictor.fit(training_set)
    daopredictor.save(predictor)
    return predictor.get_prestazioni().toJSON()

    #===========================================================================
    # except Exception as e:
    #     logger.error(e)
    #===========================================================================
        #raise CustomHttpException(*GENERIC_ERROR("create_model"))
    

def feedback(info:InterfaceInputFeedBack) -> str:
    log.debug(info)
    model=daopredictor.get_by_id(nome_modello)
    for i in range(20):
        df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n", " ")],'label': [info.label.replace("\n", " ")]})
        model.partial_fit(df)
    daopredictor.update(model)
    return "OK"



def analyzer(info:InterfaceInputModel) -> str:
    log.info('''ANALISI NEWS''')
    model = daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n"," ")]})
    prest = model.predict_proba(df)
    prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
    log.info(json.loads(prest.to_json(orient='records')))
    return json.loads(prest.to_json(orient='records'))


def info()->List[Info]:
    ''' Ritorna tutte le informazioni sui modelli esistenti'''
    #===========================================================================
    # try:
    #===========================================================================
    logger.info("informazioni")
    response=list()
    for _id in daopredictor.all():
        p=daopredictor.get_by_id(_id)
        p.id=_id
        response.append(Info(p.id, p.date, p.get_prestazioni(),p.preprocessing.language).toJSON())
        daopredictor.delete_from_memory(p.id)
    return response
    #===========================================================================
    # except Exception as e:
    #     logger.error(e)
    #     raise CustomHttpException(*GENERIC_ERROR("info"))
    #===========================================================================
    

def destroy(nome_modello:str)->str:
    ''' Elimina un analizzatore usando id '''
    daopredictor.delete(nome_modello)
    logger.info("rimuovi modello "+nome_modello)
    return "MODEL %s DELETED"%nome_modello
   
def get_languages() -> List[Language]:
    l= list()
    l.append(Language("en","English","True"))
    l.append(Language("it","Italian","True"))
    l.append(Language("es","Spanish","True"))
    #l.append(Language("pt","Portuguese",True))
    #l.append(Language("el_GR","Greek",False))
    return l



########################################################################################
#---------------------> annotation services<---------------------------------------
def next_news(lang:str) -> News:
    log.debug(lang)
    try:
        news=dao_news.next(languages=lang)
        list_author_score = []
        aut=ast.literal_eval(news.authors)
        print(len(news.authors), len(aut),aut)
        for i in aut:
            list_author_score.append({ "author" : i, "score" : dao_authors.outout_author_organization(i)})
        print(list_author_score)
        news.authors = list_author_score
   
    except StopIteration:
        return {"END":"True",
            "title":"ALL NEWS ANNOTATED"}
    return news
 # News('news1','www.thegurdian.uk','sono il titolo', 'ciao, sono il testo','sono lautore', 'sono lente')

#VERREBBE CHIAMATO DAL SISTEMA IN REGIME
def new_annotation(annotation:News_annotated) -> str:
    log.debug('id: {id}, label: {lbl}'.format(id= annotation.id, lbl=annotation.label))
    #annotation.type_annotation="A"
    print("nuova ANNOTAZIONI")
    dao_news.set_label(annotation.id, annotation.label,"M")
    return 'DONE'


def domain_annotation(list_u:News_domain) -> str:
    dao_news.create_source(list_u)
    log.debug("New domain source to annotate reiceived :{sou}".format(sou=list_u))  
    return( "DONE")


def new_doc_annotation(new_record:New_news_annotated) -> str:
    news_crawled = crawler_news(new_record.url)
    news_crawled['label'] = new_record.label
    news_crawled['language'] = new_record.lang
    news_crawled['type_annotation'] = "M"
     # new_record.type_annotation
    dao_news.create_doc_news(news_crawled)
    log.debug(news_crawled)
    return('DONE')


def new_claim_annotated(new_claim: Claims_annotated) -> str:
    print(new_claim.claim,new_claim.label)
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
    print(j_resp)
    return j_resp
    #===========================================================================
    # print(text)
    # res = dao_claim_output.get_similarity_claims_from_text(text)
    # print(res)
    # return(res)
    #===========================================================================

def info_domains()-> str:
    list_domains = dao_news.get_domain()
    return list_domains
    
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
app.add_service("info",info, method='POST')
app.add_service("destroy",destroy, method='POST')
app.add_service("info_domains",info_domains, method='GET')

CORS(app)

log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT))
app.setup()
app.run(host="0.0.0.0", port=AppConfig.BASEPORT,debug=False)
