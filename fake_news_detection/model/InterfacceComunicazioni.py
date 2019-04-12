'''
Created on Oct 18, 2018

@author: daniele
'''


   
######################ONLINE SERVICES TEST##############
class News_raw:
    def __init__(self,authors:list,date_created:str,date_modified:str,date_published:str,description:str,fakeness:str,images:list,keywords:list,language:str,source_domain:str,summary:str,text:str,texthash:str,title:str,top_image:str,url:str, version:str, video:list):
        self.authors = authors
        self.date_created = date_created
        self.date_modified = date_modified
        self.date_published = date_published
        self.description = description
        self.fakeness = fakeness
        self.images = images
        self.keywords = keywords
        self.language = language
        self.source_domain = source_domain
        self.summary = summary
        self.text = text
        self.texthash = texthash
        self.title = title
        self.top_image = top_image
        self.url = url
        self.version = version
        self.video = video


class News_DataModel:
    
    def __init__(self,headline:str,articleBody:str,dateCreated:str,dateModified:str,datePublished:str,author:list,publisher:list,  calculateRating: int,
                 calculateRatingDetail:str,images:list, video:list, sourceDomain:list):
        self.headline = headline
        self.articleBody = articleBody
        self.dateCreated = dateCreated
        self.dateModified = dateModified
        self.datePublished = datePublished
        self.author = author
        self.publisher = publisher
        self.images = images
        self.video = video
        self.sourceDomain = sourceDomain
        self.calculateRatingDetail = calculateRatingDetail
        self.calculateRating = calculateRating
    def __str__(self):
        return "headline:"+self.headline+";articleBody:"+self.articleBody+";dateCreated:"+self.dateCreated+";dateModified:"+self.dateModified+";datePublished:"+self.datePublished+";author:"+self.author+";publisher:"+self.publisher+";about:"+self.about+";mentions:"+self.mentions+";contains:"+self.contains

class Author_org_DataModel:
    def __init__(self,identifier:str,author:list,publisher:list):
        self.identifier = identifier
        self.author = author #id list
        self.publisher = publisher #id list 
    
    def __str__(self):
        return "identifier:"+self.identifier+";author:"+self.author+";publisher:"+self.publisher
    
class Images_DataModel:
    def __init__(self,identifier:str, images:list):
        self.identifier = identifier
        self.images = images
    
    def __str__(self):
        return "identifier:"+self.identifier+";images:"+self.images


class Videos_DataModel:
    def __init__(self, identifier:str, videos:list):
        self.identifier = identifier
        self.videos = videos
        
        
class Topics_DataModel:
    def __init__(self, identifier:str,mentions:list,contains:list):
        self.identifier = identifier
        self.mentions = mentions
        self.contains = contains
        


###############################################################
    
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
    
        
