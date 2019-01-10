'''
Created on 18 ott 2018

@author: michele
'''
import pickle
from fake_news_detection.config.AppConfig import picklepath


class ModelDAO(object):
    '''
    classdocs
    '''          
            
            
    def load(self,nome):
        path=picklepath +"/"+ str(nome) + ".p"
        print(path)
        try:
            with open(path, 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File not found "+path)
    
        
        
        
    
                    
            
        