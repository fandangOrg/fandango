'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizFlask import DS4BizFlask
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel,\
    InterfaceInputFeedBack
from fake_news_detection.dao.PickleDao import ModelDao
from fake_news_detection.business.Model import SklearnModel
from flask_cors.extension import CORS
import json
from fake_news_detection.config import AppConfig
from fake_news_detection.config.AppConfig import static_folder
from fake_news_detection.utils.Crawler import crawler_news
from flask import request
from fake_news_detection.business.IndexLiar import IndexLiar

oo = ModelDao() 
model = oo.load('test')
    
    
def feedback(info:InterfaceInputFeedBack)->str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    text=info.text.replace("\n"," ")
    model.partial_fit(info.title,text,info.label)
    return "OK"

 
def analyzer(info:InterfaceInputModel)->str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    print(info.title,info.text)
    text=info.text.replace("\n"," ")
    prest=model.predict(info.title,text)
    print(json.loads(prest.to_json(orient='records')))
    
    return json.loads(prest.to_json(orient='records'))

def crawler(url:str)->str:
    print(url)
    return crawler_news(url)

def claim():
    j = request.get_json()  #key txt of the dictionary
    text = j.get("text")
    #I = IndexLiar()
    #j_resp = I.similarClaims(text, max_claims=5)
    j_resp = ["ciao test 1","ciao test 2 "]
    return j_resp

app=DS4BizFlask(__name__,static_folder=static_folder+"/",static_url_path="/web")
app.root="/fandango/v0.1/fakeness"
app.name="FANDANGO"
app.add_service("analyzer",analyzer, method='POST')
app.add_service("cr_url",crawler, method='POST')
app.add_service("feedback",feedback, method='POST')
app.add_service("claim", claim, method = 'POST')

CORS(app)


print("RUN ON ",AppConfig.BASEURL,AppConfig.BASEPORT)
app.run(host="0.0.0.0", port=AppConfig.BASEPORT,debug=False)
