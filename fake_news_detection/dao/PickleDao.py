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


    def __init__(self, params):
        '''
        Constructor
        '''
        self.accepted_answers = set(["y", "n"])
    
    def Save(self, modello, nome=None):
        if nome == None:
            print("Please enter a name for the model")
            nome = input()
        output_path = picklepath + str(nome) + ".p"
        self.checkPath(nome, modello, output_path)
        
        
    def checkPath(self, nome, modello, output_path):    
        if os.path.exists(output_path):
            print("The name you have chosen {name} already exists. Would you like to owerwrite it? y/n".format(name =nome))
            typed = input()
            self.checkTyped(typed, modello, output_path)
        else:
            return pickle.dump( modello , open( output_path, "wb" ) )
            
            
            
            
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
            output_path = picklepath + str(nome) + ".p"
            self.checkPath(nome, modello, output_path)
            
            
    def load(self,nome):
        
    
                    
            
        