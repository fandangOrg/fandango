from polyglot.text import Text
from abc import ABC, abstractmethod
from fake_news_detection.config.constants import LANG_SUPPORTED
import numpy as np
from math import log
from string import punctuation


class FeaturesExtractor(ABC):
    def __init__(self, lang:str):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__

    @abstractmethod
    def __call__(self, text:str) -> int:
        pass


class PunctuationCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            count = 0
            for p in punctuation:
                if p in text:
                    count += 1
            return log(count + 1)
        except:
            return np.nan


class CharsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            return log(len(text) + 1)
        except:
            return np.nan


class WordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for word in doc.words]) + 1)
        except:
            return np.nan


class SentencesCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([sentence for sentence in doc.sentences]) + 1)
        except:
            return np.nan


class PositiveWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == 1]) + 1)
        except:
            return np.nan


class NegativeWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == -1]) + 1)
        except:
            return np.nan

class PositiveWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == 1]) + 1)
        except:
            return np.nan


class SentimentWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            pos = 0
            neg = 0
            for word in doc.words:
                if word.polarity == +1:
                    pos += 1
                elif word.polarity == -1:
                    neg += 1
            return log(pos+1) - log(neg+1)
        except:
            return np.nan


class EntitiesCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len(doc.entities) + 1)
        except:
            return np.nan
