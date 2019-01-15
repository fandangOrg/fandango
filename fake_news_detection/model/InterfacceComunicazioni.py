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
    def __init__(self, id:str, label:str):
        self.id = id
        self.label = label
  

        
class News_domain:
    def __init__(self, label:str,list_url:str, lang:str):
        self.label = label
        self.list_url = list_url
        self.lang = lang
        
        
        
        
class New_news_annotated:
    def __init__(self,url:str, label:str, lang:str):
        self.url = url
        self.label = label
        self.lang = lang
        
    
class Claim:
    def __init__(self, label, claim, author):
        self.label = label
        self.claim = claim
        self.author = author        
        


