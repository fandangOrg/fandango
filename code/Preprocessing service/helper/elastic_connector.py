# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 14:50:31 2019

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 12:40:40 2018

@author: user
"""
import elasticsearch as elast
import elasticsearch.helpers as helpers
from elasticsearch.helpers import bulk
import pandas as pd
from models.author import Author
from models.organization import Organization
from fuzzywuzzy import fuzz
from helper import global_variables as gv


class ElasticSearchConnector():
    def __init__(self, host,port, username=None, password=None):
        
        # ====================================================
        # --------------- PARAMETERS ELASTICSEARCH CONNECTOR
        # ====================================================
        # host: stored host
        # port: ElasticSearch Port
        # username: associated user to cluster
        # password: associated password to cluster
        # es: elasticSearch object
        # indexes: list of elastic indexes
        # raw_data: data extracted from elastic that has not been preprocessed

        self.host = host
        self.port = port
        self.password = password
        self.username = username
        self.es = None
        self.indexes = None
        self.raw_data = None

    def connect(self):
        ok=True

        # -------------------------------------
        #         # ------------ DOCKER ----------------
        #         #os.system('./tunnel_elastic.sh')
        #         # -------------------------------------

        try:
            self.es = elast.Elasticsearch([{'host': self.host, 'port': self.port}],max_retries=2,
                                          http_compress=True)
            if self.es.ping(request_timeout=1):
                gv.logger.info('Connected to ElasticSearch at \'%s:%s\'.',self.host,self.port)
            else:
                gv.logger.info('It was not possible to connect to \'%s:%s\'.', self.host,self.port)
                ok=False
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok

    def search(self, index_name, search):
        res = None
        try:
            res = self.es.search(index=index_name, body=search)
        except Exception as e:
            gv.logger.error(e)
        return res
    
    def get_indexes(self):
        self.indexes = list(self.es.indices.get_alias("*").keys())
        return self.indexes

    def extract_data_from_elasticSearch(self, index, query, doc_type='article'):
        try:
            print('Extracting data from index {} of FANDANGO\'s elasticSearch ...'.format(index))
            # 1) Get total number of elements
            items = helpers.scan(self.es, query=query, index=index, doc_type=doc_type)
            self.raw_data = self.parse_data(items, index)
        except Exception as e:
            gv.logger.error(e)
        return self.raw_data

    def extract_info_item(self, item):
        item_dict = {}
        item_dict['id'] = item['_id']
        item_dict['type'] = item['_type']
        item_dict['source'] = item['_source']
        return item_dict
    
    def parse_data(self, items, index):
        df_data = None
        data = []
        try:
            for item in items:
                data.append(self.extract_info_item(item))
            # Create two DataFrames
            df_info = pd.DataFrame(data)
            df_source = pd.DataFrame.from_records(df_info.source.values.tolist(),
                                                  coerce_float =True)
            df_info.drop(['source'], axis=1, inplace=True)
            
            # Concatenate DataFrames and add the ElasticSearch Index
            df_data = pd.concat([df_info, df_source], axis=1)
            df_data['index'] = index
        except Exception as e:
            gv.logger.error(e)
        return df_data

    def retrieveArticleIdentifierById(self, id):
        try:
            results = self.es.get(index=gv.idf_es_index,doc_type="doc",id=id)
            # Check results from generator
            return results['_source']
        except Exception as e:
            gv.logger.error(e)
            response = {}
        return response

    def retrieveAuthor(self, name):
        response = Author(name=name)
        try:
            query = {"query": {"match": {"name":{"query": name,"fuzziness":"0"}}}}
            results = self.es.search(body=query, index=gv.person_es_index)
            # Check results from generator
            if results['hits']['total'] > 0:
                # Compute distance
                res_name = results['hits']['hits'][0]['_source']['name']
                distance = fuzz.ratio(res_name.replace(' ', '').lower(), name.replace(' ', '').lower())
                if distance >=95:
                    response = Author.from_dict(results['hits']['hits'][0]['_source'],
                                                results['hits']['hits'][0]['_id'])

        except Exception as e:
            gv.logger.error(e)
            response = Author(name=name)
        return response

    def retrieveAuthorById(self, id):
        try:
            results = self.es.get(index=gv.person_es_index,doc_type="doc",id=id)
            # Check results from generator
            return results['_source']
        except Exception as e:
            gv.logger.error(e)
            response = {}
        return response

    def retrieveOrganization(self, name):
        response = Organization(name=name)
        try:
            query = {"query": {"match": {"name":{"query": name,"fuzziness":"0"}}}}
            results = self.es.search(body=query, index=gv.org_es_index)
            if results['hits']['total'] > 0:
                res_name = results['hits']['hits'][0]['_source']['name']
                distance = fuzz.ratio(res_name.replace(' ', '').lower(), name.replace(' ', '').lower())
                if distance >= 95:
                    response = Organization.from_dict(results['hits']['hits'][0]['_source'],
                                                      results['hits']['hits'][0]["_id"])
        except Exception as e:
            gv.logger.error(e)
            response = Organization(name=name)
        return response

    def retrieveOrganizationById(self, id):
        try:
            results = self.es.get(index=gv.org_es_index,doc_type="doc",id=id)
            # Check results from generator
            return results['_source']
        except Exception as e:
            gv.logger.error(e)
            response = {}
        return response

    def createAuthor(self, author):
        response = ""
        try:
            actions = [{'_index': gv.person_es_index,
                        '_type': "doc",
                        '_source': author.to_dict(id=False)}]
            bulk(self.es, actions)
            query = {"query": {"match": {"name":{"query": author.name,"fuzziness":"0"}}}}
            results = self.es.search(body=query, index=gv.person_es_index)
            if results['hits']['total'] > 0:
                res_name = results['hits']['hits'][0]['_source']['name']
                distance = fuzz.ratio(res_name.replace(' ', '').lower(), author.name.replace(' ', '').lower())
                # Check Distance
                if distance >= 95:
                    response = results['hits']['hits'][0]['_id']
        except Exception as e:
            gv.logger.error(e)
            response = ""
        return response

    def createOrganization(self, organization):
        response = ""
        try:
            actions = [{'_index': gv.org_es_index,
                        '_type': "doc",
                        '_source': organization.to_dict(id=False)}]
            res = bulk(self.es, actions)
            if res:
                query = {"query": {"match": {"name": {"query": organization.name, "fuzziness": "0"}}}}
                results = self.es.search(body=query, index=gv.org_es_index)
                if results['hits']['total'] > 0:
                    res_name = results['hits']['hits'][0]['_source']['name']
                    distance = fuzz.ratio(res_name.replace(' ', '').lower(), organization.name.replace(' ', '').lower())
                    # Check Distance
                    if distance >= 95:
                        response = results[0]['hits']['hits'][0]['_id']
        except Exception as e:
            gv.logger.error(e)
            response = ""
        return response

    def insertDataframeIntoElastic(self, dataFrame, index='index', doc_type = 'article'):
        ok=True
        try:
            if not self.es.indices.exists(index=index):
                    self.es.indices.create(index=index,body={})
            
            def generate_dict(df):
                records = df.to_dict(orient='records')
                for record in records:
                    yield record
            df = dataFrame.copy()
            df = df.astype('str')
            
            documents = ({'_index': index,
                          '_type': doc_type,
                          '_id': record['id'],
                          '_source': record}
                    for record in generate_dict(df))

            gv.logger.info('Inserting Data into FANDANGO ElasticSearch ... Index: %s', index)
            bulk(self.es, documents)

        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok