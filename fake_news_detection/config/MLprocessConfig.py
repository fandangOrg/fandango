from fake_news_detection.business.textPreprocessing import TextPreprocessor
from fake_news_detection.config.constants import QUOTES
from fake_news_detection.business.featuresExtraction import  CharsCounter, PunctuationCounter,\
    StopwordCounter, LexicalDiversity, AveWordxParagraph, FleschReadingEase,\
    FKGRadeLevel, SentencesCounter, CountAdv, CountAdj, CountPrep_conj,\
    countVerbs, AVGWordsCounter, AVGSentencesSizeCounter, POSDiversity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from ds4biz_predictor_core.model.creation_requests import CreationRequest,\
    PipelineRequest
from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory,\
    ScikitPredictorFactory
from typing import Union
from ds4biz_predictor_core.model.transformers.transformers import ColumnTransformer


lang_code = "en"
lang_name = "english"

#preprocess=TextPreprocessor(lang=lang_code, mode="lemmatization", rm_stopwords=True, invalid_chars=QUOTES, encoding="utf-8")

def text_preprocessing_mapping(preprocess):
    return  [
            ('text', preprocess),
            ('title', preprocess)
            ]
#(lang=lang_code)

class app_str:
    def __init__(self,name,lang_code):
        self.__name__= name
        self.lang=lang_code
        
def new_features_mapping(lang_code):
    return  [
                                #('text', CharsCounter(lang=lang_code)),
                                #('title', CharsCounter(lang=lang_code)),
                                ("text",app_str("rix",lang_code)),
                                ("text",app_str("lix",lang_code)),
                                ("text",app_str("gunning_fog",lang_code)),
                                ("text",app_str("dale_chall_readability_score",lang_code)),
                                ("text",app_str("linsear_write_formulas",lang_code)),
                                ("text",app_str("automated_readability_index",lang_code)),
                                ("text",app_str("coleman_liau_index",lang_code)),
                                ("text",app_str("smog_index",lang_code)),
                                ("text",app_str("flesch_kincaid_grade",lang_code)),
                                ("text",app_str("vflesch_reading_ease",lang_code)),
                                ("text",app_str("avg_sentence_per_word",lang_code)),
                                ("text",app_str("avg_letter_per_word",lang_code)),
                                ("text",app_str("avg_character_per_word",lang_code)),
                                ("text",app_str("avg_syllables_per_word",lang_code)),
                                ###
                                # #
                                ###
                                ("title",app_str("avg_sentence_length",lang_code)),
                                ("title",app_str("avg_sentence_per_word",lang_code)),
                                ("title",app_str("avg_letter_per_word",lang_code)),
                                ("title",app_str("avg_character_per_word",lang_code)),
                                ("title",app_str("avg_syllables_per_word",lang_code)),
                                ###
                                # #
                                ###
                                
                                ('text', AVGSentencesSizeCounter(lang=lang_code)),
                                ('title', AVGWordsCounter(lang=lang_code)),
                                ('text', AVGWordsCounter(lang=lang_code)),
                                ('text', PunctuationCounter(lang=lang_code)),
                                ('title', PunctuationCounter(lang=lang_code)),
                                ('title', StopwordCounter(lang= lang_code)),
                                ('text',LexicalDiversity(lang = lang_code)),
                                #('text', FleschReadingEase(lang = lang_code)),
                                #('text', FKGRadeLevel(lang = lang_code)),
                                ('text', POSDiversity(lang = lang_code)),
                                ('title', POSDiversity(lang = lang_code)),

                                #('text', SentencesCounter(lang=lang_code)),
                                ('text', StopwordCounter(lang = lang_code)),
                                ('text', AveWordxParagraph(lang = lang_code)),
                                ('text', CountAdv(lang = lang_code)),
                                ('text', CountAdj(lang = lang_code)),
                                ('text', CountPrep_conj(lang = lang_code)),
                                ('text', countVerbs(lang = lang_code))
                                #('text', PositiveWordsCounter(lang=lang_code)),
                                #('text', NegativeWordsCounter(lang=lang_code)),
                                #('text', SentimentWordsCounter(lang=lang_code)),
                                #('text', EntitiesCounter(lang=lang_code))
                                #('title', EntitiesCounter(lang=lang_code)                ]
            ]
#(min_df=10, ngram_range=(1, 2), stop_words=lang_name, lowercase=True)
transforming_mapping = {
                         'title': TfidfVectorizer,
                         'text': TfidfVectorizer,
                         'text_StopwordCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_CharsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'title_CharsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_PunctuationCounter': MinMaxScaler(feature_range=(0, 1)),
                         'title_PunctuationCounter': MinMaxScaler(feature_range=(0, 1)),
                         'text_StopwordCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_LexicalDiversity' : MinMaxScaler(feature_range=(0, 1)),
                         'text_AveWordxParagraph' : MinMaxScaler(feature_range=(0, 1)),
                         'text_FleschReadingEase' : MinMaxScaler(feature_range=(0, 1)),
                         'text_FKGRadeLevel' : MinMaxScaler(feature_range=(0, 1)),
                         'text_SentencesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_CountAdv' : MinMaxScaler(feature_range=(0, 1)),
                         'text_CountAdj': MinMaxScaler(feature_range=(0, 1)),
                         'text_CountPrep_conj' : MinMaxScaler(feature_range=(0, 1)),
                         'text_countVerbs' : MinMaxScaler(feature_range=(0, 1))
                         #'text_PositiveWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'text_NegativeWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'text_EntitiesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'title_EntitiesCounter': MinMaxScaler(feature_range=(0, 1))
                         #'text_SentimentWordsCounter' : MinMaxScaler(feature_range=(0, 1))
                       }


### CLASSIFIERS ###

#name_classifier = "MultinomialNB"
#params_classifier = {'alpha':0.5}

#name_classifier = "SGDClassifier"
#params_classifier = {'loss':"log", "max_iter":10, 'n_jobs':-1}

class ConfigFactory:
    def __init__(self):
        self.configurations=dict()
         
    def register_config(self,project,config_name,clf_conf:CreationRequest ):
        conf_project=self.configurations.get(project,{})
        conf_project[config_name]=clf_conf
        
        self.configurations[project]=conf_project

    def create_model_by_configuration(self,project,config_name):
        try:
            clf_conf= self.configurations[project][config_name]
            return TransformingPredictorFactory().create(clf_conf,CreationRequest("MinMaxScaler" ))
        except: 
            raise Exception("Configuration don't exist",project,config_name)




config_factory=ConfigFactory()
request_model1 = CreationRequest("SGDClassifier", {'loss':'log', 'max_iter':10, 'penalty':'elasticnet', 'tol':0.001,  'n_jobs':-1})
request_model2 = CreationRequest("BernoulliNB", {'alpha':0.175, 'binarize':0.15, 'fit_prior':True})
request_model3 = CreationRequest("ComplementNB", {'alpha':0.575, 'norm':True})
request_model4 = CreationRequest("MultinomialNB", {'alpha':0.75, 'fit_prior':False})
config_factory.register_config("fandango","1", request_model1)
config_factory.register_config("fandango","2", request_model2)
config_factory.register_config("fandango","3", request_model3)
config_factory.register_config("fandango","4", request_model4)










