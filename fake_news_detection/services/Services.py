'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizFlask import DS4BizFlask
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel
from fake_news_detection.dao.PickleDao import ModelDao
from fake_news_detection.business.Model import SklearnModel
from flask_cors.extension import CORS
import json
from fake_news_detection.config import AppConfig

 
oo = ModelDao()
model = oo.load('test')
    
    

 
 
def analyzer(info:InterfaceInputModel)->str:
    print(info)
    '''Creazione di un nuovo analizzatore per i social'''
    print(info.title,info.text)
    prest=model.predict(info.title,info.text)
    print(json.loads(prest.to_json(orient='records')))
    
    return json.loads(prest.to_json(orient='records'))


app=DS4BizFlask(__name__,static_folder="/home/daniele/progetti/fandango-fake-news/static/",static_url_path="/web")
app.root="/fandango/v0.1/fakeness"
app.name="FANDANGO"
app.add_service("analyzer",analyzer, method='POST')
CORS(app)


@app.route( '/module.js' )
def baseurl():
    url = AppConfig.BASEURL+":"+AppConfig.BASEPORT
    return '''var app = angular.module('app', []);
                var base = "%s/fandango/v0.1/fakeness";
                '''%url
 
print("RUN ON ",AppConfig.BASEURL,AppConfig.BASEPORT)
app.run(host="0.0.0.0", port=AppConfig.BASEPORT,debug=True)
