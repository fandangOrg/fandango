'''
Created on 11 mar 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel,\
    News_DataModel
from fake_news_detection.utils.logger import getLogger
import pandas as pd
import json
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO



log = getLogger(__name__) 



def analyzer(daopredictor,nome_modello,news_preprocessed:News_DataModel) -> str:
    log.info('''ANALISI NEWS''')
    model = daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [news_preprocessed.headline], 'text': [news_preprocessed.articleBody.replace("\n"," ")]})
    print(df.columns)
    prest = model.predict_proba(df)
    print(prest)
    prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
    log.info(json.loads(prest.to_json(orient='records')))
    return json.loads(prest.to_json(orient='records'))

    #return (prest[0][1])
  
  
  
  
          
if __name__ == '__main__':
    
    daopredictor = FSMemoryPredictorDAO(picklepath)
    info_news = News_DataModel(headline="hi", articleBody = "how are you ", sourceDomain = 'www',identifier = "", dateCreated = "" , dateModified="", datePublished = "", author = "", publisher = "", calculateRating = "", calculateRatingDetail = "", images ="", video = "")
    nome_modello="english_try_version"
    print(info_news)
    #output= analyzer(daopredictor,nome_modello,info_news) 
    print(analyzer(daopredictor,nome_modello,info_news)[0]['REAL'])  #prendo la probabilità che sia vera
    
    