from ds4biz_predictor_core.model.creation_requests import CreationRequest
from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory
from ds4biz_predictor_core.dao.predictor_dao import FSPredictorDAO
import pandas as pd
from ds4biz_predictor_core.model.predictors.predictors import TransformingPredictor
from sklearn.base import TransformerMixin, ClassifierMixin
from sklearn.model_selection import RepeatedKFold, cross_val_score
import numpy as np
from fake_news_detection.dao.TrainingDAO import get_train_dataset


def create_configuration_for_ds4biz_predictor_core(name_classifier:str=None, params_classifier:dict={}, name_transformer:str=None, params_transformer:dict={}) -> TransformingPredictor:
    request_transformer = CreationRequest(name_transformer, params_transformer)
    request_model = CreationRequest(name_classifier, params_classifier)
    return TransformingPredictorFactory().create(request_model, request_transformer)


def fit_with_ds4biz_predictor_core(conf:TransformingPredictor, X, y):
    if type(X) != pd.core.series.Series and type(X) != list:
        raise ValueError("Invalid input 'X' in 'fit_with_ds4biz_predictor_core'!")
    if type(y) != pd.core.series.Series and type(y) != list:
        raise ValueError("Invalid input 'y' in 'fit_with_ds4biz_predictor_core'!")
    conf.fit(X, y)


def partial_fit_with_ds4biz_predictor_core(conf:TransformingPredictor, X, y):
    if type(X) != pd.core.series.Series and type(X) != list:
        raise ValueError("Invalid input 'X' in 'partial_fit_with_ds4biz_predictor_core'!")
    if type(y) != pd.core.series.Series and type(y) != list:
        raise ValueError("Invalid input 'y' in 'partial_fit_with_ds4biz_predictor_core'!")
    if not conf.fitted:import
        raise Exception("It is not possible to call 'partial fit' before 'fit'!")
    if not conf.is_partially_fittable:
        raise Exception("The chosen model is not partialy fittable!")
    conf.partial_fit(X, y)


def predict_with_ds4biz_predictor_core(conf:TransformingPredictor, X_new) -> list:
    if type(X_new) != pd.core.series.Series and type(X_new) != list:
        raise ValueError("Invalid input 'X_new' in 'predict_with_ds4biz_predictor_core'!")
    return conf.predict(X_new)


def predict_probabilities_with_ds4biz_predictor_core(conf:TransformingPredictor, X_new) -> list:
    if type(X_new) != pd.core.series.Series and type(X_new) != list:
        raise ValueError("Invalid input 'X_new' in 'predict_probabilities_with_ds4biz_predictor_core'!")
    return conf.predict_proba(X_new)


def evaluate_trought_CV_with_ds4biz_predictor_core(conf:TransformingPredictor, X, y, metric:str="accuracy", num_fold:int=5, num_iterations:int=1, seed:int=1) -> float:
    X_transformed = conf.transformer.transform(X)
    rep_k_fold = RepeatedKFold(n_splits=num_fold, n_repeats=num_iterations, random_state=seed)
    scores = cross_val_score(conf.predictor.predictor, X_transformed, y, cv=rep_k_fold, scoring=metric)
    final_score = np.mean(scores)
    print(metric, final_score)
    return final_score


def evaluate_with_ds4biz_predictor_core(conf:TransformingPredictor) -> dict:
    diz = {"accuracy":conf.predictor.accuracy, "precision":conf.predictor.precision, "recall":conf.predictor.recall}
    print("accuracy", diz["accuracy"])
    print("precision", diz["precision"])
    print("recall", diz["recall"])
    return diz

def get_scikit_transformer(conf:TransformingPredictor) -> TransformerMixin:
    return conf.transformer


def get_scikit_predictor(conf:TransformingPredictor) -> ClassifierMixin:
    return conf.predictor.predictor


def store_ds4biz_model(conf:TransformingPredictor, id:str, path:str) -> TransformingPredictor:
    conf.id = id                              #set unique name
    return FSPredictorDAO(path).save(conf)


def load_ds4biz_model(id:str, path:str) -> TransformingPredictor:
    loaded_model = FSPredictorDAO(path).get_by_id(id)
    print("\n", loaded_model.id, ":\n", loaded_model)
    return loaded_model



if __name__ == "__main__":

    X_title_new = ["title A", "title B", "title C", "title D", "title E", "title F", "title G", "title H", "title I", "title L"]
    X_text_new = [ "i worked on sunday so i had monday off",  "the desk has three drawers",
                   "he is about your age", "yes but i still don't have many friends here yet",
                   "where are you", "i can't figure out what she really wants",
                   "it's none of my business", "mary can dance well",
                   "don't be absurd", "i'll show you around the city" ]
    X_new = pd.Series(X_title_new).map(str) + ' ' + pd.Series(X_text_new).map(str)

    ### merge 'title' and 'text' columns and set X and y ###
    training_set = get_train_dataset()
    #training_set = training_set.sample(frac=0.05)   # sampling for quickly test
    X = training_set['title'].map(str) + ' ' + training_set['text'].map(str)
    y = training_set['label']
    print('\n training_set', training_set.shape, "\n X", X.shape, "\n y", y.shape)

    ### create configuration ###
    conf = create_configuration_for_ds4biz_predictor_core("MultinomialNB", {'alpha':0.5},
                                                          "TfidfVectorizer", {'stop_words':'english', 'ngram_range':(2, 3), 'lowercase':True, 'min_df':2})
    ### train ###
    fit_with_ds4biz_predictor_core(conf, X, y)

    ### incremental train ###
    partial_fit_with_ds4biz_predictor_core(conf, ["USA president is a martian Donald Trump is an alien"], ["FAKE"])

    ### prediction ###
    prediction = predict_with_ds4biz_predictor_core(conf, X_new)
    print("\n prediction", prediction)
    probabilities = predict_probabilities_with_ds4biz_predictor_core(conf, X_new)
    print("\n probability distribuition of classes: \n", conf.predictor.predictor.classes_)
    print(probabilities)

    ### get scikit-learn objects ###
    print("\n Transformer", get_scikit_transformer(conf))
    print("\n Classificator", get_scikit_predictor(conf))

    ### evaluation ###
    print("\n Holdout method (80% train | 20% test)")
    evaluate_with_ds4biz_predictor_core(conf)
    print("\n 5-fold cross validation")
    evaluate_trought_CV_with_ds4biz_predictor_core(conf, X, y)     # accuracy 0.953

    ### store and load from disk ###
    store_ds4biz_model(conf, id="clf-fandango", path="/home/camila/workspace/fandango-fake-news/fake_news_detection/resources/model")
    load_ds4biz_model(id="miao", path="/home/camila/workspace/fandango-fake-news/fake_news_detection/resources/model")
