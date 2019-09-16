'''
Created on 23 apr 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import News_DataModel, Author_org_DataModel, Media_DataModel, Topics_DataModel,\
 InterfaceInputFeedBack, Claim_input, Claim_output, News, News_annotated
from ds4biz_commons.utils.requests_utils import URLRequest
from fake_news_detection.config.AppConfig import  static_folder, url_service_media,\
    url_service_authors, url_similar_claims, template_path,\
    static_folder_annotation
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
######################## ANNOTATION SERVICES ###########################
dao_annotation=DAOElasticAnnotation()
 
#---------------------> annotation services<---------------------------------------
def next_news(lang:str,author:str) -> News:
    log.debug(lang)
    try:
        news=dao_annotation.next_news(author,language=lang)
   
    except StopIteration:
        return {"END":"True",
            "title":"ALL NEWS ANNOTATED"}
    return news

def new_annotation(annotation:News_annotated) -> str:
    log.debug('id: {id}, label: {lbl}'.format(id= annotation.id, lbl=annotation.label))
    print("nuova ANNOTAZIONI")
    dao_annotation.insert_new_annotation(annotation.id, annotation.author, 
                                         annotation.language, annotation.label)
    return 'DONE'

def counterAnnotations() -> int:
    print("counter Annos")
    j = request.get_json()
    lang = j.get('language')
    return(dao_annotation._get_counter_annoation(lang))

def get_languages() -> List[Language]:
    l= list()
    l.append(Language("en","English","True"))
    l.append(Language("it","Italian","True"))
    l.append(Language("es","Spanish","True"))
    #l.append(Language("pt","Portuguese",True))
    #l.append(Language("el_GR","Greek",False))
    return l
#===============================================================================

###run deamon

#daemon_run()

headers = {'content-type': "application/json",'accept': "application/json"}
    
    
    
#------------------------------------>DECODING ELASTIC ID SERVICES<----------------------------------

app=DS4BizFlask(__name__,static_folder=static_folder_annotation+"/dist/",static_url_path="",template_folder='../templates/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html')


app.root="/fandango/v0.3/fakeness"
app.name="FANDANGO"
app.add_service("next_news", next_news, method ='POST')
app.add_service("new_annotation", new_annotation, method = 'POST')
app.add_service("counter_annotations", counterAnnotations, method= 'POST')
app.add_service("get_languages",get_languages, method = 'GET')

CORS(app)
log.info("RUN ON {cfg}".format(cfg= AppConfig.BASEURL+AppConfig.BASEPORT_ANNOTATION))
app.setup()
app.run(host = "0.0.0.0", port = AppConfig.BASEPORT_ANNOTATION,debug=False)





