from fake_news_detection.business.textPreprocessing import TextPreprocessor
from fake_news_detection.config.constants import QUOTES
from fake_news_detection.business.featuresExtraction2 import PositiveWordsCounter, NegativeWordsCounter, EntitiesCounter, WordsCounter, SentencesCounter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

lang_code = "en"
lang_name = "english"

text_preprocessing_mapping = [
                                ('text', TextPreprocessor(lang=lang_code, mode="lemmatization", rm_stopwords=True, invalid_chars=QUOTES, encoding="utf-8")),
                                ('title', TextPreprocessor(lang=lang_code, mode="lemmatization", rm_stopwords=True, invalid_chars=QUOTES, encoding="utf-8"))
                             ]

new_features_mapping = [
                            ('text', WordsCounter(lang=lang_code)),
                            ('text', SentencesCounter(lang=lang_code)),
                            ('text', PositiveWordsCounter(lang=lang_code)),
                            ('text', NegativeWordsCounter(lang=lang_code)),
                            ('text', EntitiesCounter(lang=lang_code)),
                            ('title', EntitiesCounter(lang=lang_code))
                        ]

transforming_mapping = {
                         'title': TfidfVectorizer(min_df=10, stop_words=lang_name, lowercase=True),
                         'text': TfidfVectorizer(min_df=15, ngram_range=(2, 3), stop_words=lang_name, lowercase=True),
                         'text_WordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_SentencesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_PositiveWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_NegativeWordsCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'text_EntitiesCounter' : MinMaxScaler(feature_range=(0, 1)),
                         'title_EntitiesCounter': MinMaxScaler(feature_range=(0, 1))
                       }

name_classifier_1 = "MultinomialNB"
params_classifier_1 = {'alpha':0.5}

name_classifier_2 = "SGDClassifier"
params_classifier_2 = {'loss':"log", "max_iter":100, 'n_jobs':-1}