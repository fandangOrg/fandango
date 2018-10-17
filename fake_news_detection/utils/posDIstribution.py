'''
Created on 4 ott 2018

@author: camila
'''
from fake_news_detection.dao.ElasticDao import Search
from fake_news_detection.resources.Treetaggerservice import Tagga
from fake_news_detection.utils.logger import getLogger
import requests
import re





class posDistribution(object):
    '''
    classdocs
    '''

    
    


    def __init__(self):
        '''
        Constructor
        '''
        self.Search = Search()
        
        self.log = getLogger(__name__)
        self.langdict = frozenset(["en", "it", "el", "nl"])
        self.problem = frozenset(["AWQdyUZCiQ1kzMRG_jjU","AWQdyeICiQ1kzMRG_jpp","AWQdyc0ciQ1kzMRG_jo1", 'AWQdyRMsiQ1kzMRG_jhP', 'AWQdyKgJiQ1kzMRG_jc5', 'AWQdyUapiQ1kzMRG_jjV', 'AWQdyTuAiQ1kzMRG_ji3', 'AWQdyI3TiQ1kzMRG_jb0','AWQdxww-iQ1kzMRG_jL6', 'AWQdwF3eiQ1kzMRG_iFU'])
    
    def posDistribution(self,):
        
        all_doc = self.Search.DownloadAll()
        dic_pos_distribution = {}
        
        
        lista_azioni = []
        for c,i in enumerate(all_doc):
            self.log.debug(c)
            self.log.info("items found:{it}".format(it = i['_id']))
            """
            if str("AWQdyUZCiQ1kzMRG_jjU") in str(i['_id']):
                print("#########################")
                continue
            if str("AWQdyeICiQ1kzMRG_jpp") in str(i['_id']):
                print("#########################")
                continue
            elif str("AWQdyc0ciQ1kzMRG_jo1") in str(i['_id']):
                print("#########################")
                continue
            elif str('AWQdyRMsiQ1kzMRG_jhP') in str(i['_id']):
                print("#########################")
                continue 
            elif str('AWQdyKgJiQ1kzMRG_jc5') in str(i['_id']):
                print("#########################")
                continue
            elif str('AWQdyUapiQ1kzMRG_jjV') in str(i['_id']):
                print("#########################")
                continue
            elif str('AWQdyTuAiQ1kzMRG_ji3') in str(i['_id']):
                print("#########################")
                continue
            """
            
            
            
            if i['_source']['language'] in self.langdict:
                
                print(i['_id'], i)
                
                if i['_id'] in self.problem:
                    self.cleanText(i)
                    phrase_taggedL = self.tretagger_call_problematic(i)
                elif "AWQdxr6LiQ1kzMRG_jIr" in i['_id']:
                    print("cazzooooooooooo!")
                    continue
                else:
                    phrase_taggedL = self.tretagger_call(i)

                #dic_pos_distribution[i['_id']] = self.pos_distribution(phrase_taggedL)
                
                lista_azioni = self.populateElastic(i, phrase_taggedL, lista_azioni)
                
            else:
                self.log.info("Item with id {idd} has not supported language: {lan}".format(idd=i['_id'], lan=i['_source']['language']))
                continue
            
        print("Preparazione finita")
        indicizza=self.Search.BulkNewIndex(lista_azioni)

        
        
    def tretagger_call(self,i):
        #te = self.T.trasforms(i['_source']['text'].split())
        try:
            out_treetagger = requests.post("http://localhost:8080/tag?lang={lan}".format(lan= i['_source']['language']),json={"text": i['_source']['text']})
                
        except Exception as e:
            self.log.debug("PROBLEMA: {e}".format(e= e))
            raise e  
        return out_treetagger.json()
    
    
    def tretagger_call_problematic(self,i):
        output =[]
        #te = self.T.trasforms(i['_source']['text'].split())
        try:
            for part in i['_source']['text'].split("\n"):
                part = " ".join([pez for pez in part if pez[0] != "<"])
                out_treetagger = requests.post("http://localhost:8080/tag?lang={lan}".format(lan= i['_source']['language']),json={"text":part})
                output.extend( out_treetagger.json() )
                
        except Exception as e:
            self.log.debug("PROBLEMA: {e}".format(e= e))
            raise e  
        return output
    
    def pos_distribution(self, output_treetagger):
        dic = {}
        
        for item in output_treetagger:
            if item[1] in dic:
                dic[item[1]] += 1
            else :
                dic[item[1]] = 1

        return dic
    
    def populateElastic(self, i , phrase_taggedL, lista_azioni):
        crea_indice = self.Search.CreateNewIndex()
        lingua = i['_source']['language']
        i["_source"]["text_{ln}".format(ln=lingua)] = i["_source"]["text"]
        del i["_source"]["text"]
        i["_source"]["title_{ln}".format(ln=lingua)] = i["_source"]["title"]
        del i["_source"]["title"]
        lista_azioni = self.Search.AddNewFieldsandINDEX(i, phrase_taggedL, crea_indice, lista_azioni)
        return lista_azioni
    
    def cleanText(self, i):
        patternDaMatchare = re.compile("<.*?>")
        i['text'] = patternDaMatchare.sub(r" ", i['text'] )
        print( i['text'] )
        
        
        
        

        
        
    
            
            
if __name__  == "__main__":
    p = posDistribution()
    p.posDistribution()
    del p 
    
        
        
        
    