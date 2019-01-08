'''
Created on 27 set 2018

@author: camila
'''

from fake_news_detection.config.AppConfig import index_name_news, get_elastic_connector,\
    docType, mapping, index_name_claims
from fake_news_detection.utils.logger import getLogger
from elasticsearch import helpers
import csv
from elasticsearch.helpers import bulk


class Search:
    def __init__(self): 
        self.ESclient = getEsConnector()
        self.index_name = new_mapped_index #news_article_current
        self.docType = docType   
        self.log = getLogger(__name__) #richiamo la funzione scritta nel log 
        
        #helper aiutano alla combinazioni di queries
        

    def GetNextElements(self, bookmark):
        
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
        res = self.ESclient.search(index=self.index_name, body= body1)
        for el in res['hits']['hits']:
            if el is not None:
                yield el['_source']
            else:
                try:
                    bookmark = [res['hits']['hits'][-1]['sort'][0], str(res['hits']['hits'][-1]['sort'][1])]
                    self.GetNextElements(bookmark)  
                except Exception as e:
                    self.DownloadAll()          
    
    
    def DownloadAll(self):
        
        
        body = { "size": 10,
                    "query": {
                        "match":{"label": ""}
                        }
                    ,
                    "sort": [
                        {"date_download": "desc"},
                        {"url": "desc"}
                    ]
                }
        
        result = self.ESclient.search(index=self.index_name , body= body)
        for res in result['hits']['hits']:
            if res:
                yield res['_source']
        else:
            try:                
                bookmark = [result['hits']['hits'][-1]['sort'][0], str(result['hits']['hits'][-1]['sort'][1])]
                self.GetNextElements(bookmark)
            except Exception as e:
                self.DownloadAll()
        

        
    def delete(self):
        try:
            self.ESclient.indices.delete(self.index_name)
        except:
            pass
            
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
                      "minimum_should_match": "80%",
                      "must": [
                        {
                          "match": {
                            "claim": text
                          }
                        }
                      ]
                    }
                  }
                    ,
                    "highlight" : {
                        "pre_tags" : ["<b>"],
                        "post_tags" : ["</b>"],
                        "fields" : {
                            "claim" : 
                                {
                                 "number_of_fragments":0
                                }
                        }
                    }
                }
        
        res = self.ESclient.search(index= self.index_name, body= body1)
        l =[]
        for r in res['hits']['hits']:
            print(r)
            if r["_score"]>5:
                d=r['_source']
                d['_score']=r["_score"]
                d["claim"]=r["highlight"]["claim"][0]
                l.append(d) 
            
        return l
    
    
    def CreateNewIndex(self):
        try:
            self.ESclient.indices.delete_template("template_segnalazioni")
        except:
            pass
        
        if not self.ESclient.indices.exists(index=new_mapped_index):
            mapping_path = mapping
            with open(mapping_path , "r") as f:
                map = f.read()
                print(map)
                try:
                    self.ESclient.indices.create(index = new_mapped_index, body = map)
                except:
                    self.log.info("Could not create new index: {ind}".format(ind = new_mapped_index))
                    print(new_mapped_index)
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
                
                
                #print(fields)
                
                lista_azioni.append( {
                    '_op_type': 'index',
                    '_index': crea_indice,
                    '_type': self.docType,
                    '_source': fields
        
                })
    
        return lista_azioni
    
    def _bulk_items(self,items):
        for  source_dict in items:
            yield source_dict
            #===================================================================
            # yield {'_op_type': 'index',
            # '_index': self.collection,
            #  'refresh':'wait_for',
            # '_type': '_doc',
            # '_source': source_dict
            # }
            #===================================================================
                
        
    #===========================================================================
    # def BulkNewIndex(self,lista_azioni):
    #     #self.client.commit(self.collection, openSearcher=True)
    #     bulk(self.ESclient, self._bulk_items([x for x in lista_azioni]))
    #===========================================================================
         
    def BulkNewIndex(self, lista_azioni):
        for success, info in helpers.parallel_bulk(self.ESclient, lista_azioni):
            if not success:
                print(info)

                
        self.log.info("New index successfully indexed")

    
        
        
        
                    
        