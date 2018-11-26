'''
Created on 27 set 2018

@author: camila
'''

from fake_news_detection.config.AppConfig import index_name, getEsConnector,\
    pathFileLastDate, docType, mapping, new_mapped_index
from fake_news_detection.utils.logger import getLogger
from elasticsearch import helpers
import csv


class Search( ):
#prendo il connettore
    def __init__(self): 
        self.ESclient = getEsConnector()
        self.index_name = new_mapped_index
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
    
    
     #change between body or body if you want to use or or and operation among words in the 
    def similarity_query(self,text):
        
        body = {
                "query": {
                    "match_phrase": {
                        "claim": text
                        }
                    }
                }
        
        body1 = {
                  "query": {
                    "bool": {
                      "should": [
                        {
                          "match_phrase": {
                            "claim": text
                          }
                        }
                      ],
                      "filter": [
                        {
                          "match": {
                            "claim": text
                          }
                        }
                      ]
                    }
                  }
                }
        
        res = self.ESclient.search(index= self.index_name, body= body1)
        l =[]
        for r in res['hits']['hits']:
            l.append(r['_source']) 
            
        return l
    
    
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
    
    def AddNewFieldsandINDEX(self,csv_file, crea_indice, lista_azioni):
            
        with open(csv_file) as f:
            reader = csv.reader(f, delimiter='\t')
            for r in reader:
                #print(r)
            
                    #print(row.split('/t'))
                fields ={}
                        
                fields["id_jason"] = r[0]
                fields["label"] =  r[1]
                fields["claim"] =  r[2]
                fields["topic"] = r[3]
                fields["author"] = r[4]
                fields["role_of_the_authore"] = r[5]
                
                
                print(fields)
                
                lista_azioni.append( {
                    '_op_type': 'index',
                    '_index': crea_indice,
                    '_type': self.docType,
                    '_source': fields
        
                })
    
        return lista_azioni
    
    def BulkNewIndex(self, lista_azioni):
        for success, info in helpers.parallel_bulk(self.ESclient, lista_azioni):
            if not success:
                print(info)

                
        self.log.info("New index successfully indexed")

    
        
        
        
                    
        