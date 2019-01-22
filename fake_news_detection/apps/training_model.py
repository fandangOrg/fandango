'''
Created on Jan 22, 2019

@author: daniele
'''
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath, dataset_beta
from fake_news_detection.utils.mlUtils import create_trasformer_predictor
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD
from sklearn.model_selection._split import train_test_split


daopredictor=FSMemoryPredictorDAO(picklepath)
def training():
    training_set = DAOTrainingPD().get_train_dataset()
    X = training_set['title'].map(str) + ' ' + training_set['text'].map(str)
    y = training_set['label']
    #    model.train(X_train['title'],X_train['text'], y_train['label'],X_train)
    config=["MultinomialNB", {'alpha':0.5},"TfidfVectorizer", {'stop_words':'english', 'ngram_range':(2, 3), 'lowercase':True, 'min_df':2}]
    
    modello_en=create_trasformer_predictor(*config)
    modello_en.id="modello_en"
    modello_en.fit(X, y)
    daopredictor.save(modello_en)


def test(nome_modello):
    training_set = DAOTrainingPD().get_train_dataset()
    X = training_set['title'].map(str) + ' ' + training_set['text'].map(str)
    result=daopredictor.get_by_id(nome_modello).predict(X)
    print(result)
    
    


if __name__ == '__main__':
    test("modello_en")   