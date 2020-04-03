'''
Created on Oct 18, 2018

@author: daniele
'''

######################ONLINE SERVICES TEST##############


class Open_Data: 

    def __init__(self, text:str, category:str, topics:list):
        self.text = text
        self.category = category
        self.topics = topics
        

class News_raw:

    def __init__(self, identifier:str, date_published: str, authors:list, date_created:str, date_modified:str, description:str,
                 images:list, keywords:list, language:str, source_domain:str, summary:str, text:str, texthash:str,
                 title:str, top_image:str, url:str, videos:list, spider:str, publish_date_estimated:bool):
        self.identifier = identifier
        self.authors = authors
        self.publish_date_estimated = publish_date_estimated
        self.date_created = date_created
        self.date_modified = date_modified
        self.date_published = date_published 
        # self.linkNumber = linkNumber
        self.description = description
        #self.fakeness = fakeness
        self.images = images
        self.keywords = keywords
        self.language = language
        self.source_domain = source_domain
        print(source_domain)
        self.summary = summary
        self.text = text
        self.texthash = texthash
        self.title = title
        self.top_image = top_image
        self.url = url
        self.videos = videos
        self.spider = spider


class News_DataModel:

    def __init__(self, url:str, language:str, identifier:str, headline:str, articleBody:str, dateCreated:str, dateModified:str, datePublished:str, author:list, publisher:list, calculateRating: int,
                 calculateRatingDetail:str, images:list, videos:list,
                 sourceDomain:list, country:str, nationality:str,
                 publishDateEstimated:bool,
                  video_analizer:bool=False,
                  image_analizer:bool=False, **kwargs:dict):
        self.url = url
        self.headline = headline
        self.articleBody = articleBody
        self.dateCreated = dateCreated
        self.dateModified = dateModified
        self.datePublished = datePublished
        self.author = author
        self.publisher = publisher
        self.images = images
        self.videos = videos
        print("SORUCE DOMAIN", type(sourceDomain), sourceDomain)
        if type(sourceDomain)is list:
            self.sourceDomain = sourceDomain[0]
        else:
            self.sourceDomain = sourceDomain
        self.calculateRatingDetail = calculateRatingDetail
        self.calculateRating = calculateRating
        self.identifier = identifier
        self.language = language
        self.country = country
        self.nationality = nationality
        self.video_analizer = video_analizer
        self.image_analizer = image_analizer
        self.publishDateEstimated = publishDateEstimated
        # self.fakeness=fakeness

    '''
    def __str__(self):
        return "headline:"+self.headline+";articleBody:"+self.articleBody+";dateCreated:"+self.dateCreated+";dateModified:"+self.dateModified+";datePublished:"+self.datePublished+";author:"+self.author+";publisher:"+self.publisher
    '''


class Author_org_DataModel:

    def __init__(self, identifier:str, author:list, publisher:list, authorRating:list=[], publisherRating:list=[], **kwargs:dict):
        self.identifier = identifier
        self.author = author  # id list
        self.publisher = publisher  # id list
        self.authorRating = authorRating
        self.publisherRating = publisherRating 
    
    def __str__(self):
        return "identifier:" + self.identifier + ";author:" + self.author + ";publisher:" + self.publisher

    
class Media_DataModel:

    def __init__(self, identifier:str, images:list, videos:list):
        self.identifier = identifier
        self.images = images
        self.videos = videos
    
    def __str__(self):
        return "identifier:" + self.identifier + ";images:" + self.images

        
class Topics_DataModel:

    def __init__(self, identifier:str, topic:str, mentions:list, about:list):
        self.identifier = identifier
        self.mentions = mentions
        self.about = about
        self.topic = topic

        
class Final_DataModel:

    def __init__(self, identifier:str, headline:str, articleBody:str, dateCreated:str, dateModified:str, datePublished:str, author:list, publisher:list, calculatedRating: int,
                 calculatedRatingDetail:str, images:list, videos:list, sourceDomain:str, mentions:list, about:list, videosanal:dict, imagesanal:dict):
        self.identifier = identifier
        self.headline = headline
        self.articleBody = articleBody
        self.dateCreated = dateCreated
        self.dateModified = dateModified
        self.datePublished = datePublished
        self.author = author
        self.publisher = publisher
        self.calculatedRating = calculatedRating
        self.calculatedRatingDetail = calculatedRatingDetail
        self.images = images
        self.videos = videos
        self.sourceDomain = sourceDomain
        self.mentions = mentions
        self.about = about


class OutputVideoService:

    def __init__(self, video_id:str, status:str="UNKNOW", url:str="UNKNOW", fakeness: float=0.5, video_url:str="UNKNOW"
                 , reasoning:list=["UNKNOW", "UNKNOW"], first_frame:int=0, last_frame:int=100, fps:int=12, prograssMax:float=0.0):
        self.status = status
        self.video_id = video_id
        self.url = url
        self.fakeness = fakeness
        self.video_url = video_url
        self.reasoning = reasoning
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.fps = fps
        self.prograssMax = prograssMax
        
        
class OutputImageService:

    def __init__(self, image_id:str, status:str="UNKNOW", url:str="UNKNOW", fakeness:float=0.5):
        
        self.status = status
        self.image_id = image_id
        self.url = url
        self.fakeness = fakeness
    
        
class OutputAuthorService:

    def __init__(self, name:str, jobTitle:str="UNKNOW", url:str="UNKNOW", affiliation:str="", trustworthiness:float=0.0, **args):
        self.name = name
        self.jobTitle = jobTitle
        self.url = url
        self.affiliation = affiliation
        self.fakenessScore = trustworthiness

            
class OutputPublishService:

    def __init__(self, name:str, url:str="UNKNOW", affiliation:str="", trustworthiness:float=0.0, **args):
        self.name = name
        self.url = url
        self.affiliation = affiliation
        self.fakenessScore = trustworthiness

###############################################################

    
class InterfaceInputModel:
    
    def __init__(self, title:str, text:str, source:str):
        self.title = title
        self.text = text
        self.source = source
        

class InterfaceInputFeedBack:
    
    def __init__(self, title:str, text:str, label:str):
        self.title = title
        self.text = text
        self.label = label
        

class News:

    def __init__(self, url:str, title:str, text:str, authors:str, source_domain:str, language:str=None, id:str=None):
        self.url = url
        self.title = title
        self.text = text
        self.authors = authors
        self.source_domain = [source_domain]
        self.language = language
        self.id = id
          
    def __str__(self):
        return  "id: " + self.id + "; url: " + self.url + "; title: " + self.title + "; text: " + self.text.replace("\n", " ")


class News_annotated:

    def __init__(self, id:str, label:str, author:str=None, language:str=None):
        self.id = id
        self.label = label
        self.author = author
        self.language = language
 
        
class News_domain:

    def __init__(self, label:str, list_url:str, lang:str):
        self.label = label
        self.list_url = list_url
        self.lang = lang
        
        
class New_news_annotated:

    def __init__(self, url:str, label:str, lang:str, type_annotation:str=None):
        self.url = url
        self.label = label
        self.type_annotation = type_annotation
        self.lang = lang
        
    
class Claim_input:

    def __init__(self, identifier:str, text:str, topics:list):
        self.identifier = identifier
        self.text = text
        self.topics = topics


class Claim_output:

    def __init__(self, identifier:str, topics:list, results:list):
        self.identifier = identifier
        self.results = results
        self.topics = topics
      
    
class Claims_annotated:

    def __init__(self, claim:str, label:str):
        self.claim = claim
        self.label = label   


class Prestazioni:
    
    def __init__(self, precision:float, recall:float, accuracy:float, number_item:int):
        self.precision = precision
        self.recall = recall
        self.accuracy = accuracy
        self.number_item = number_item
        
    def toJSON(self):
        return self.__dict__


class UploadImageInput:

    def __init__(self, url:str, image:str):
        self.url = url
        self.image = image
    

class Info:

    def __init__(self, nome_modello:str, data_creazione:str, prestazioni:Prestazioni, language:str):
        self.nome_modello = nome_modello
        self.data_creazione = data_creazione
        self.prestazioni = prestazioni
        self.language = language

    def toJSON(self):
        # return self.__dict__
        return {"nome_modello":self.nome_modello,
                "data_creazione": self.data_creazione,
                "language": self.language,
                "prestazioni":self.prestazioni.toJSON()}
        
