'''
Created on Oct 18, 2018

@author: daniele
'''
from ds4biz_flask.model.DS4BizTyping import DS4BizList

    
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
    def __init__(self, url:str, title:str, text:str, authors:str, source_domain:str, id:str=None ,language:str=None ):
        self.url = url
        self.title = title
        self.text = text
        self.authors = authors
        self.source_domain = source_domain
        self.id = id
        self.language = language


    def __str__(self):
        return  "id: "+self.id+"; url: "+self.url+"; title: "+self.title+"; text: "+self.text.replace("\n"," ")

class News_annotated:
    def __init__(self, id:str, label:str):
        self.id = id
        self.label = label
    

        
class News_domain:
    def __init__(self, label:str,list_url:str):
        self.label = label
        self.list_url = list_url
        
        
        
        
class New_news_annotated:
    def __init__(self,url:str, label:str, lang:str):
        self.url = url
        self.label = label
        self.lang = lang
        
    
        
        


