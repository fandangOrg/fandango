'''
Created on 11 mar 2019

@author: camila
'''
from fake_news_detection.model.InterfacceComunicazioni import InterfaceInputModel
from fake_news_detection.utils.logger import getLogger
import pandas as pd
import json
log = getLogger(__name__) 


def analyzer(info:InterfaceInputModel,daopredictor,nome_modello) -> str:
    log.info('''ANALISI NEWS''')

    model = daopredictor.get_by_id(nome_modello)
    df = pd.DataFrame(data={'title': [info.title], 'text': [info.text.replace("\n"," ")]})
    prest = model.predict_proba(df)
    prest = pd.DataFrame(prest, columns=model.predictor_fakeness.predictor.predictor.classes_)
    log.info(json.loads(prest.to_json(orient='records')))
    #return json.loads(prest.to_json(orient='records'))
    return (prest)
