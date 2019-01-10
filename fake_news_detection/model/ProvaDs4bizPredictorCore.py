import nltk
from ds4biz_predictor_core.model.creation_requests import CreationRequest
from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory
from ds4biz_predictor_core.dao.predictor_dao import FSPredictorDAO
import pandas as pd
from ds4biz_predictor_core.model.predictors.predictors import TransformingPredictor
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from scipy.sparse import hstack
from fake_news_detection.dao.TrainingDAO import get_train_dataset


def create_configuration_for_ds4biz_predictor_core():
    request_tf_idf = CreationRequest("TfidfVectorizer", {'stop_words': 'english', 'ngram_range': (2, 3)})
    request_model1 = CreationRequest("MultinomialNB", {'alpha': 0.05})
    return TransformingPredictorFactory().create(request_model1, request_tf_idf)

def fit_with_ds4biz_predictor_core(conf: TransformingPredictor, X, y):
    return conf.fit(X, y)

def predict_with_ds4biz_predictor_core(conf: TransformingPredictor, X_new):
    return conf.predict(X_new)

def get_scikit_transformer(conf: TransformingPredictor):
    return conf.transformer

def get_scikit_predictor(conf: TransformingPredictor):
    return conf.predictor.predictor

def store_ds4biz_model(conf: TransformingPredictor, id: str, path: str):
    conf.id = id  # set unique name
    return FSPredictorDAO(path).save(conf)

def load_ds4biz_model(id: str, path: str):
    loaded_model = FSPredictorDAO(path).get_by_id(id)
    print("\n", loaded_model.id, ":\n", loaded_model)
    return loaded_model



if __name__ == "__main__":

    X_title_new = [
        "title A",
        "title B",
        "title C",
        "title D",
        "title A",
        "title A",
        "title E",
        "title B",
        "title C",
        "title C"
    ]

    X_text_new = [
        "i worked on sunday so i had monday off",
        "the desk has three drawers",
        "he is about your age",
        "yes but i still don't have many friends here yet",
        "where are you",
        "i can't figure out what she really wants",
        "it's none of my business",
        "mary can dance well",
        "don't be absurd",
        "i'll show you around the city"
    ]

    training_set = get_train_datasetet()
    conf = create_configuration_for_ds4biz_predictor_core()
    X_final = hstack([X_text, X_title])
    ds4biz_model = fit_with_ds4biz_predictor_core(conf, X_final, y)
    X_final_new = hstack([X_text_new, X_title_new])
    prediction = predict_with_ds4biz_predictor_core(conf, X_new)
    print("\n")
    print(prediction)
    print(get_scikit_transformer(conf))
    print(get_scikit_predictor(conf))
    store_ds4biz_model(conf, id="miao", path="/home/andrea/")
    load_ds4biz_model(id="miao", path="/home/andrea/")