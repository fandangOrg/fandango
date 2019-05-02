'''
Created on 14 mar 2019

@author: daniele
'''
from nltk.corpus import stopwords

from time import sleep
from threading import Thread
import functools
import threading

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


