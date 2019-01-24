import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.utils.mlUtils import create_trasformer_predictor, create_trasformer_predictor_2
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD


daopredictor=FSMemoryPredictorDAO(picklepath)


# def training(model_name:str):
#     training_set = DAOTrainingPD().get_train_dataset(sample_size=1.0)
#     X = training_set['title'].map(str) + ' ' + training_set['text'].map(str)
#     y = training_set['label']
#     config=["MultinomialNB", {'alpha':0.5}, "TfidfVectorizer", {'stop_words':'english', 'ngram_range':(2, 3), 'lowercase':True, 'min_df':2}]
#     model = create_trasformer_predictor(*config)
#     model.id = model_name
#     model.fit(X, y)
#     daopredictor.save(model)
#     print("Accuracy:", model.predictor.accuracy)
#     print("Precision:", model.predictor.precision)
#     print("Recall:", model.predictor.recall)


def training(model_name:str):
    training_set = DAOTrainingPD().get_train_dataset(sample_size=1.0)
    X = training_set[['title', 'text']]
    y = training_set['label']
    model = create_trasformer_predictor_2(name_classifier = "MultinomialNB",
                                         params_classifier = {'alpha':0.5},
                                         transformer_title = TfidfVectorizer(min_df=10, stop_words='english', lowercase=True),
                                         transformer_text = TfidfVectorizer(min_df=15, ngram_range=(2, 3), stop_words='english', lowercase=True))
    model.id = model_name
    model.fit(X, y)
    daopredictor.save(model)
    print("Training of '" + model_name + "': DONE")
    print("   - Accuracy:", model.predictor.accuracy)
    print("   - Precision:", model.predictor.precision)
    print("   - Recall:", model.predictor.recall)


def predict(nome_modello):
    training_set = DAOTrainingPD().get_train_dataset()
    X = training_set[['title', 'text']]
    prediction = daopredictor.get_by_id(nome_modello).predict(X)
    print(prediction)


def predict_proba(nome_modello):
    training_set = DAOTrainingPD().get_train_dataset()
    X = training_set[['title', 'text']]
    prob_distribution = daopredictor.get_by_id(nome_modello).predict_proba(X)
    print(daopredictor.get_by_id(nome_modello).predictor.predictor.classes_)
    np.set_printoptions(formatter={'float_kind': '{:f}'.format})
    print(prob_distribution)


if __name__ == '__main__':
    #training(model_name="modello_en_2")
    predict("modello_en_2")
    predict_proba("modello_en_2")