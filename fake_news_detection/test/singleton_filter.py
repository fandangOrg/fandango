'''
Created on 14 mar 2019

@author: daniele
'''
from nltk.corpus import stopwords

from threading import Thread
import functools
import threading
import treetaggerwrapper
from fake_news_detection.config.constants import LANG_MAPPING
from nltk.stem.snowball import SnowballStemmer
import spacy

lock = threading.Lock()
lock_2 = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """

    def wrapper(f):

        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)

        return inner_wrapper

    return wrapper


class Singleton(type):
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton_Filter(metaclass=Singleton):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.lang = ['en', 'it', 'es', "nl"]
        self.nlp_tool = dict()
        for lang in self.lang:
            print("---loading ", lang)
            self.nlp_tool[lang + "_tagger"] = treetaggerwrapper.TreeTagger(TAGLANG=lang)
            self.nlp_tool[lang + "_stopwords"] = set(stopwords.words(LANG_MAPPING[lang][0]))
            
            # self.nlpt_tool[lang+"_stemmer"] = SnowballStemmer(LANG_MAPPING[lang][1])
            # self.nlpt_tool[lang+"_nlp"] = spacy.load(LANG_MAPPING[lang][2], disable=["tagger", "parser", "ner"])

