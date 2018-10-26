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
        