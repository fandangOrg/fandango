'''
Created on 11 mar 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel
from fake_news_detection.utils.logger import getLogger
import pandas as pd
import json
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
log = getLogger(__name__) 


def analyzer(info:InterfaceInputModel,daopredictor,nome_modello) -> str:
    log.info('''ANALISI NEWS''')

    model = daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n"," ")]})
    print(df.columns)
    prest = model.predict_proba(df)
    #prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
    #log.info(json.loads(prest.to_json(orient='records')))
    #return json.loads(prest.to_json(orient='records'))
    return (prest[0][1])

    
if __name__ == '__main__':
    
    daopredictor = FSMemoryPredictorDAO(picklepath)
    info_news = InterfaceInputModel(title="hi", text = "how are you ", source = 'www')
    nome_modello="english_try_version"
    print(info_news)
    output= analyzer(info_news,daopredictor,nome_modello) 
    print(output)  #prendo la probabilità che sia vera
    
    