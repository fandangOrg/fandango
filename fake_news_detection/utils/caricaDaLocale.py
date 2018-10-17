from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json


class Upload:
    def __init__(self):
        self.path_json = r"/home/michele/Scrivania/dump_fandango"
        self.es = Elasticsearch("localhost:9200")
        
    def run(self):
        with open(self.path_json, "r") as f:
            jsonObj = json.load(f)
            print(jsonObj.keys())
            
if __name__ == '__main__':
    oo = Upload()
    oo.run()
    del oo 
            
        