'''
Created on Oct 18, 2018

@author: daniele
'''

    
class InterfaceInputModel:
    
    def __init__(self,title:str,text:str,source:str):
        self.title = title
        self.text = text
        self.source = source
        

class InterfaceInputFeedBack:
    
    def __init__(self,title:str,text:str,label:str):
        self.title = title
        self.text = text
        self.label = label
        
        
        
class News:
    def __init__(self,url:str, title:str, text:str, authors:str, source_domain:str,language:str=None,id:str=None):
        self.url = url
        self.title = title
        self.text = text
        self.authors = authors
        self.source_domain = source_domain
        self.language = language
        self.id = id
        
        


    def __str__(self):
        return  "id: "+self.id+"; url: "+self.url+"; title: "+self.title+"; text: "+self.text.replace("\n"," ")

class News_annotated:
    def __init__(self, id:str, label:str,type_annotation:str=None):
        self.id = id
        self.label = label
        self.type_annotation=type_annotation
 
        
class News_domain:
    def __init__(self, label:str,list_url:str, lang:str):
        self.label = label
        self.list_url = list_url
        self.lang = lang
        
        
        
        
class New_news_annotated:
    def __init__(self,url:str, label:str, lang:str, type_annotation:str=None):
        self.url = url
        self.label = label
        self.type_annotation = type_annotation
        self.lang = lang
        
    
class Claim:
    def __init__(self, label, claim, author):
        self.label = label
        self.claim = claim
        self.author = author        
    
class Claims_annotated:
    def __init__(self, claim:str, label:str):
        self.claim = claim
        self.label = label   



class Prestazioni:
    
    def __init__(self,precision:float,recall:float,accuracy:float,number_item:int):
        self.precision = precision
        self.recall = recall
        self.accuracy = accuracy
        self.number_item = number_item
        
    def toJSON(self):
        return self.__dict__

        

class Info:
    def __init__(self,nome_modello:str,data_creazione:str,prestazioni:Prestazioni,language:str):
        self.nome_modello = nome_modello
        self.data_creazione = data_creazione
        self.prestazioni = prestazioni
        self.language = language

    def toJSON(self):
        #return self.__dict__
        return {"nome_modello":self.nome_modello,
                "data_creazione": self.data_creazione,
                "language": self.language,
                "prestazioni":self.prestazioni.toJSON()}
    
        
