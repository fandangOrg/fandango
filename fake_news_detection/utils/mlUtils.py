'''
Created on Jan 22, 2019

@author: daniele
'''
from ds4biz_predictor_core.model.creation_requests import CreationRequest
from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory
from ds4biz_predictor_core.model.predictors.predictors import TransformingPredictor
from ds4biz_predictor_core.model.transformers.transformers import ColumnTransformer
from ds4biz_predictor_core.model.transformers.transformers import Transformer
from sklearn.feature_extraction.text import TfidfVectorizer


def create_trasformer_predictor(name_classifier:str=None, params_classifier:dict={}, name_transformer:str=None, params_transformer:dict={}) -> TransformingPredictor:
    request_transformer = CreationRequest(name_transformer, params_transformer)
    request_model = CreationRequest(name_classifier, params_classifier)
    return TransformingPredictorFactory().create(request_model, request_transformer)




def create_trasformer_predictor_2(name_classifier:str=None,
                                 params_classifier:dict={},
                                 transformer_title:Transformer=TfidfVectorizer(),
                                 transformer_text:Transformer=TfidfVectorizer()) -> TransformingPredictor:
    request_transformer = ColumnTransformer({'title':transformer_title, 'text':transformer_text})
    request_model = CreationRequest(name_classifier, params_classifier)
    return TransformingPredictorFactory().create(request_model, request_transformer)