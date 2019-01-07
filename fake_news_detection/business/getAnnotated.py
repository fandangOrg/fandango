'''
Created on 07 gen 2019

@author: michele
'''
from fake_news_detection.dao import ElasticDao

class getAnnotated(object):



    def __init__(self, params):
        '''
        Constructor
        '''
        
    def Investigate(self):
        query = ElasticDao()
        return query.DownloadAll()

        
        