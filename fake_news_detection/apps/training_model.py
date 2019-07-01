import pandas
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath, resources_path
from lightgbm.sklearn import LGBMClassifier
from fake_news_detection.model.predictor import Preprocessing, FakePredictor

def training_model_LGBMClassifier(lang,X):
    daopredictor = FSMemoryPredictorDAO(picklepath)
    predictor=LGBMClassifier() 
    print("crea modello")
    model=FakePredictor(predictor=predictor,preprocessing=Preprocessing(lang), id=lang)
    model.fit(X)
    daopredictor.save(model)




if __name__ == '__main__':
    
    for lang,train in [('en','default_train_v2_en.csv')]:
        print("leggi train")
        X=pandas.read_csv(resources_path+"/"+train ).iloc[:, 1:]
        training_model_LGBMClassifier(lang,X)
