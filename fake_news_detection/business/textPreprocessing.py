import string
import unicodedata
import spacy as spacy
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from fake_news_detection.config.constants import LANG_SUPPORTED, QUOTES, LANG_MAPPING
import numpy as np
import logging
from fake_news_detection.model.singleton_filter import Singleton
from fake_news_detection.test.singleton_filter import Singleton_Filter

i = 1

'''tolta perchè non possiamo applicare questo preprocessing in quanto poi servono tutti i dati puliti'''


class TextPreprocessor():

    def __init__(self, lang:str, mode:str=None, rm_stopwords:bool=False, invalid_chars:str=QUOTES, encoding:str="utf-8"):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.mode = mode
        self.rm_stopwords = rm_stopwords
        self.invalid_chars = invalid_chars
        self.encoding = encoding
        self.__name__ = self.__class__.__name__
        #=======================================================================
        # self.stopwords = stopwords.words(LANG_MAPPING[self.lang][0])
        # self.stemmer = SnowballStemmer(LANG_MAPPING[self.lang][1])
        # self.nlp = spacy.load(LANG_MAPPING[self.lang][2], disable=["tagger", "parser", "ner"])
        #=======================================================================
        singleton = Singleton_Filter()
        self.stopwords = singleton.stopwords
        self.stemmer = singleton.stemmer
        self.nlp = singleton.nlp
        self.i = 1

    def __call__(self, text:str) -> str:
        try:
            self.i += 1
            text = self.encode(text)
            text = self.remove_chars(text=text, in_tab=self.invalid_chars)

            if self.mode == "stemming":
                preprocessed_text = self.stemming(text)
            elif self.mode == "lemmatization":
                preprocessed_text = self.lemmatization(text)
            else:
                preprocessed_text = self.no_normalization(text)

            if preprocessed_text == "":
                return np.nan
            else:
                return preprocessed_text
        except Exception as e:
            logging.exception(str(e) + str(text))
            return np.nan

    def encode(self, text:str) -> str:
        if self.encoding == 'utf-8':
            return text.encode('utf-8').decode('utf-8')
        elif self.encoding == 'ascii':
            text_temp = self.text.encode('utf-8').decode('unicode-escape')
            return unicodedata.normalize('NFKD', text_temp).encode('ascii', 'replace').decode('ascii')
        else:
            raise ValueError("Invalid encoding!")

    def remove_chars(self, text:str, in_tab:str=string.punctuation) -> str:
        out_tab = " " * len(in_tab)
        table = str.maketrans(in_tab, out_tab)
        return text.translate(table)

    def stemming(self, text:str) -> str:
        doc = self.nlp(text)
        new_doc = []
        for token in doc:
            token_txt = token.text.lower().strip()
            if token.is_space or token.is_bracket or token.is_quote or (self.rm_stopwords and token.is_stop):
                continue
            if self.rm_stopwords and token_txt in self.stopwords:
                continue
            new_doc.append(self.stemmer.stem(token_txt))
        return (" ".join(new_doc)).strip()

    def lemmatization(self, text:str) -> str:
        doc = self.nlp(text)
        new_doc = []
        for token in doc:
            token_txt = token.text.lower().strip()
            if token.is_space or token.is_bracket or token.is_quote or (self.rm_stopwords and token.is_stop):
                continue
            if self.rm_stopwords and token_txt in self.stopwords:
                continue
            new_doc.append(token.lemma_.lower().strip())
        return (" ".join(new_doc)).strip()

    def no_normalization(self, text:str) -> str:
        doc = self.nlp(text)
        new_doc = []
        for token in doc:
            token_txt = token.text.lower().strip()
            if token.is_space or token.is_bracket or token.is_quote or (self.rm_stopwords and token.is_stop):
                continue
            if self.rm_stopwords and token_txt in self.stopwords:
                continue
            new_doc.append(token_txt)
        return (" ".join(new_doc)).strip()

