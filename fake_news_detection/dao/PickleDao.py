'''
Created on 18 ott 2018

@author: michele
'''
import pickle
from fake_news_detection.config.AppConfig import picklepath
import os


class ModelDao(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.accepted_answers = set(["y", "n"])
    
    def save(self, modello, nome,force=True):
        #=======================================================================
        # if nome == None:
        #     print("Please enter a name for the model")
        #     nome = input()
        #=======================================================================
        output_path = picklepath +"/"+ str(nome) + ".p"
        self.checkPath(nome, modello, output_path,force)
        
        
    def checkPath(self, nome, modello, output_path,force):    
        if os.path.exists(output_path):
            if force:
                pickle.dump( modello , open( output_path, "wb" ) )
            else:
                print("modello esistente, usare force = True per sovrascriverlo")
        else:
            pickle.dump( modello , open( output_path, "wb" ) )
            
            
            
            
    def checkTyped(self, typed, modello, output_path):
        if typed not in self.accepted_answers:
            print("Please type y or n ")
            typed = input()
            self.checkTyped(typed, modello, output_path)

        if typed.lower() == "y":
            return pickle.dump( modello , open( output_path, "wb" ) )
        elif typed.lower() == "n":
            print("Please enter a name for the model")
            nome = input()
            output_path = picklepath +"/"+ str(nome) + ".p"
            self.checkPath(nome, modello, output_path)
            
            
            
    def load(self,nome):
        path=picklepath +"/"+ str(nome) + ".p"
        try:
            with open(path, 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File not found "+path)
    
        
        
        
    
                    
            
        