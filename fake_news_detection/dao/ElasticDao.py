'''
Created on 27 set 2018

@author: camila
'''

from fake_news_detection.config.AppConfig import index_name, getEsConnector,\
    pathFileLastDate, docType, mapping, new_mapped_index
from fake_news_detection.utils.logger import getLogger
from elasticsearch import helpers



class Search( ):
#prendo il connettore
    def __init__(self): 
        self.ESclient = getEsConnector()
        self.index_name = index_name
        self.docType = docType   
        self.log = getLogger(__name__) #richiamo la funzione scritta nel log 
        
        #helper aiutano alla combinazioni di queries
        
        
    """
    def DownloadAll(self):
        body2 = {"query": {"match_all":{}}}
        
    
        res = self.ESclient.count(index= self.index_name, body= body2)
        size = res['count']
        
        body = {"query":{"match_all":{}},"size": size}
        
        result = self.ESclient.search(self.index_name,self.docType, body= body)
        for res in result['hits']['hits']:
            yield res['_source']
        
        
    """
    def DownloadAll(self):
        
        
        body2 = {"query": {"match_all":{}}}
        
    
        res = self.ESclient.count(index= self.index_name, body= body2)
        size = res['count']
        
        
        body = { "size": 10,
                    "query": {
                        "match_all":{}
                        }
                    ,
                    "sort": [
                        {"date_download": "desc"},
                        {"url": "desc"}
                    ]
                }
        
        result = self.ESclient.search(index=self.index_name , body= body)
        bookmark = [result['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1])]
        
        body1 = {"size": 10,
                    "query": {
                        "match_all":{}
                        }
                    ,
                    "search_after": bookmark,
                    "sort": [
                        {"date_download": "desc"},
                        {"url": "desc"}
                       
                    ]
                }
        
        
        
        
        while len(result['hits']['hits']) < size:
            res = self.ESclient.search(index=self.index_name, body= body1)
            for el in res['hits']['hits']:
                result['hits']['hits'].append( el )
            bookmark = [res['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1])]
            body1 = {"size": 10,
                    "query": {
                        "match_all":{}
                        }
                    ,
                    "search_after": bookmark,
                    "sort": [
                        {"date_download": "desc"},
                        {"url": "desc"}
                    ]
            
                }


        return result['hits']['hits']
        

            
    def DownloadPartial(self):
        
        try:
            with open(pathFileLastDate, 'r') as p:
                lastdate = p.read()
                
        except Exception as e:
            self.log.info("could'nt read from file :{e}".format(e = e))
            raise e
            
            
        
        
        body1 = {
                "query": {
                    "range": {
                      "WARC_Date": {
                        "gte": lastdate
                      }
                    }
                  }
                }
        
        result = self.ESclient.search(index=self.index_name , body= body1)
        self.log.info("UPDATED")
        return result               
    
    
    def GetLastDate(self):
        
        body = {"size" : 0,
              "aggs": {
                "datamaggiore": {
                  "max": {
                    "field": "WARC_Date"
                  }
                }
              }
            }
        
        res = self.ESclient.search( index=self.index_name , body= body)
        lastdate = res['aggregations']['datamaggiore']['value_as_string']
        with open(pathFileLastDate,"w") as f:
            f.write(lastdate)
            self.log.info("File successfully written: date = {date}".format(date = lastdate))
        return lastdate
    
    def CreateNewIndex(self):
        if not self.ESclient.indices.exists(index=new_mapped_index):
            mapping_path = mapping
            with open(mapping_path , "r") as f:
                map = f.read()
                try:
                    self.ESclient.indices.create(index = new_mapped_index, body = map)
                except:
                    self.log.info("Could not create new index: {ind}".format(ind = new_mapped_index))
                    raise "Could not create new index: {ind}".format(ind = new_mapped_index)
        return new_mapped_index
    
    def AddNewFieldsandINDEX(self, i , phrase_taggedL, crea_indice, lista_azioni):
        taggedL = []
        for item in phrase_taggedL:
            new_nested ={"word": item[0],
                         "pos": item[1],
                         "lemma": item[2].rstrip()
                            }
            taggedL.append(new_nested)
        i["_source"]["pos_tag"] = taggedL
        lista_azioni.append( {
                '_op_type': 'index',
                '_index': crea_indice,
                '_type': self.docType,
                '_source': i['_source'],
                '_id': i['_id']
            })
        return lista_azioni
    
    def BulkNewIndex(self, lista_azioni):
        for success, info in helpers.parallel_bulk(self.ESclient, lista_azioni):
            if not success:
                print(info)

                
        self.log.info("New index successfully indexed")
    
    

        
        
        
                    
        