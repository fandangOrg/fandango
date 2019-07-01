import pandas
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath, resources_path
from lightgbm.sklearn import LGBMClassifier
from fake_news_detection.model.predictor import Preprocessing, FakePredictor
from keras.wrappers.scikit_learn import KerasClassifier
from fake_news_detection.test.keras_no_deep import create_model1

def training_model_LGBMClassifier(lang,X):
    daopredictor = FSMemoryPredictorDAO(picklepath)
    predictor=LGBMClassifier() 
    print("crea modello")
    model=FakePredictor(predictor=predictor,preprocessing=Preprocessing(lang), id=lang)
    model.fit(X)
    daopredictor.save(model)


def training_model_KerasClassifier(lang,X):
    input_dim = X.shape[1]-3
    use_dense_vectors = True
    epochs = 200
    batch_size = int(8507/20)+1

    daopredictor = FSMemoryPredictorDAO(picklepath)
    predictor=KerasClassifier(build_fn=create_model1,input_dim=input_dim, epochs=epochs, batch_size=batch_size, verbose=1) 
    print("crea modello")
    model=FakePredictor(predictor=predictor,preprocessing=Preprocessing(lang), id=lang)
    model.fit(X)
    daopredictor.save(model)



if __name__ == '__main__':
    
    for lang,train in [('it','default_train_v2_en.csv')]:
        print("leggi train")
        X=pandas.read_csv(resources_path+"/"+train ).iloc[:, 1:]
        training_model_KerasClassifier(lang,X)
