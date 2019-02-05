from fake_news_detection.business.textPreprocessing import TextPreprocessor
from fake_news_detection.config.constants import QUOTES
from fake_news_detection.business.featuresExtraction2 import PositiveWordsCounter, NegativeWordsCounter, \
    EntitiesCounter, WordsCounter, SentencesCounter, SentimentWordsCounter, CharsCounter, PunctuationCounter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from math import log


lang_code = "en"
lang_name = "english"

text_preprocessing_mapping = [
                                ('text', TextPreprocessor(lang=lang_code, mode="lemmatization", rm_stopwords=True, invalid_chars=QUOTES, encoding="utf-8")),
                                ('title', TextPreprocessor(lang=lang_code, mode="lemmatization", rm_stopwords=True, invalid_chars=QUOTES, encoding="utf-8"))
                             ]

new_features_mapping = [
                            ('text', CharsCounter(lang=lang_code)),
                            ('title', CharsCounter(lang=lang_code)),
                            ('text', PunctuationCounter(lang=lang_code)),
                            ('title', PunctuationCounter(lang=lang_code)),
                            #('text', SentencesCounter(lang=lang_code)),
                            #('text', PositiveWordsCounter(lang=lang_code)),
                            #('text', NegativeWordsCounter(lang=lang_code)),
                            #('text', SentimentWordsCounter(lang=lang_code)),
                            #('text', EntitiesCounter(lang=lang_code))
                            #('title', EntitiesCounter(lang=lang_code))
                        ]

transforming_mapping = {
                         'title': TfidfVectorizer(min_df=5, ngram_range=(1, 1), stop_words=lang_name, lowercase=True),
                         'text': TfidfVectorizer(min_df=10, ngram_range=(1, 2), stop_words=lang_name, lowercase=True),
                         'text_CharsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'title_CharsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_PunctuationCounter': MinMaxScaler(feature_range=(0, 1)),
                         'title_PunctuationCounter': MinMaxScaler(feature_range=(0, 1)),
                         #'text_SentencesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'text_PositiveWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'text_NegativeWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'text_EntitiesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         #'title_EntitiesCounter': MinMaxScaler(feature_range=(0, 1))
                         #'text_SentimentWordsCounter' : MinMaxScaler(feature_range=(0, 1))
                       }


### CLASSIFIERS ###

#name_classifier = "MultinomialNB"
#params_classifier = {'alpha':0.5}

name_classifier = "SGDClassifier"
params_classifier = {'loss':"log", "max_iter":10, 'n_jobs':-1}