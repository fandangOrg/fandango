from helper import global_variables as gv
from elasticsearch.helpers import bulk
from fuzzywuzzy import fuzz
import elasticsearch as elast
import pandas as pd
import hashlib


class ElasticsearchManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.es = None
        self.connection = False

    def connect(self):
        try:
            self.es = elast.Elasticsearch([{'host': self.host, 'port': self.port}])
            if self.es.ping(request_timeout=1):
                self.connection = True
                gv.logger.info('Connected to ElasticSearch at \'%s:%s\'.', self.host, self.port)
            else:
                self.connection = False

        except ConnectionError as ce:
            gv.logger.error(ce)
            self.connection = False
        except Exception as e:
            gv.logger.error(e)
        return self

    def get_indexes(self):
        self.indexes = list(self.es.indices.get_alias("*").keys())
        return self.indexes

    def extract_info_item(self, item):
        item_dict = {}
        try:
            item_dict['id'] = item['_id']
            item_dict['source'] = item['_source']
        except Exception as e:
            gv.logger.error(e)
        return item_dict

    def parse_data(self, items, index, add_index_col=True):
        df_data = None
        data = []
        try:
            for item in items:
                data.append(self.extract_info_item(item))

            # Create two DataFrames
            df_info = pd.DataFrame(data)
            df_source = pd.DataFrame.from_records(df_info.source.values.tolist(),
                                                  coerce_float=True)
            df_info.drop(['source'], axis=1, inplace=True)

            # Concatenate DataFrames and add the ElasticSearch Index
            df_data = pd.concat([df_info, df_source], axis=1)
            if add_index_col:
                df_data['index'] = index
        except Exception as e:
            gv.logger.error(e)
        return df_data

    def extract_data_from_elasticsearch(self, index, query, scroll="1m", size=10000):
        data = None
        try:
            gv.logger.info('Extracting data from index %s of Elasticsearch ...', index)
            items = self.scroll_data_from_elasticsearch(index=index, body=query,
                                                        scroll=scroll, size=size)
            if len(items) > 0:
                data = self.parse_data(items, index)
        except Exception as e:
            gv.logger.error(e)
        return data

    def scroll_data_from_elasticsearch(self, index, body, scroll="1m", size=1000):
        items = []
        try:
            res = self.es.search(index=index, body=body, scroll=scroll)
            if res:
                # update data
                items += res["hits"]["hits"]
                total_elements = res["hits"]["total"]["value"]
                rest_elements = (total_elements - size)
                if rest_elements > 0:
                    done = True
                    prev = res
                    while done:
                        new_items = self.es.scroll(scroll_id=prev['_scroll_id'], scroll=scroll)
                        if len(new_items["hits"]["hits"]) > 0:
                            items += new_items["hits"]["hits"]
                            prev = new_items
                        else:
                            done = False
        except Exception as e:
            gv.logger.error(e)
        return items

    def retrieve_data_from_index_by_id(self, index, uuid):
        try:
            response = self.retrieve_doc_from_index_by_id(es=self.es, index=index, uuid=uuid)
        except Exception as e:
            gv.logger.warning(e)
            response = {}
        return response

    @staticmethod
    def retrieve_doc_from_index_by_id(es, index, uuid):
        response = {}
        try:
            results = es.get(index=index, doc_type="doc", id=uuid)
            # Check results from generator
            response = results['_source']
        except Exception as e:
            gv.logger.warning(e)
        return response

    def retrieve_data_from_index_by_searching(self, index, search_key, search_value, fuzzy_threshold=95,
                                              request_timeout=30):
        response = {}
        try:
            query = {"query": {"match": {search_key: {"query": search_value, "fuzziness": "0"}}}}
            results = self.es.search(body=query, index=index, request_timeout=request_timeout)
            if results['hits']['total'] > 0:
                res_name = results['hits']['hits'][0]['_source'][search_key]
                distance = fuzz.ratio(res_name.replace(' ', '').lower(), search_value.replace(' ', '').lower())
                if distance >= fuzzy_threshold:
                    response = {"source": results['hits']['hits'][0]['_source'],
                                "id": results['hits']['hits'][0]["_id"]}
        except Exception as e:
            gv.logger.error(e)
        return response

    def bulk_data_into_index(self, index, uuid, source_data):
        response = {}
        try:
            actions = [{'_index': index,
                        '_id': uuid,
                        '_type': "doc",
                        '_source': source_data}]
            res = bulk(self.es, actions, refresh='wait_for')
            if res:
                response = self.retrieve_data_from_index_by_id(index=index, uuid=uuid)
        except Exception as e:
            gv.logger.error(e)
        return response

    def bulk_dataframe_into_index(self, data, index_name, index_col):
        try:
            def generate_dict(df):
                records = df.to_dict(orient='records')
                for record in records:
                    uuid = self.__class__.generate_uuid_from_string(data_uuid=[record[index_col]])
                    yield record, uuid

            actions = ({'_index': index_name,
                        '_type': "doc",
                        '_id': uuid,
                        '_source': record}
                       for record, uuid in generate_dict(data))
            bulk(self.es, actions, refresh='wait_for', raise_on_error=True)
        except Exception as e:
            gv.logger.error(e)
        return self

    def update_fields_to_index(self, index, uuid, body):
        try:
            self.es.update(index=index, doc_type="doc", id=uuid,
                           body=body)
        except Exception as e:
            gv.logger.error(e)

    def create_new_index(self, index, body=None):
        res = True
        try:
            if not self.es.indices.exists(index=index):
                # Simple index creation with no particular mapping
                if body is None:
                    body = {}
                self.es.indices.create(index=index, body=body)
        except Exception as e:
            gv.logger.error(e)
            res = False
        return res

    def remove_index(self, index):
        res = True
        try:
            gv.logger.info('Removing index %s from Elasticsearch', str(index))
            self.es.indices.delete(index=index, ignore=[400, 404])
        except Exception as e:
            gv.logger.error(e)
            res = False
        return res

    @staticmethod
    def generate_uuid_from_string(data_uuid):
        identifier = ""
        try:
            if len(data_uuid) == 1:
                hash_object = hashlib.sha512(data_uuid[0].encode('utf-8'))
                identifier = hash_object.hexdigest()
            elif len(data_uuid) == 2:
                identifier = hashlib.sha256(data_uuid[0].encode('utf-8')).hexdigest() + \
                             hashlib.sha256(data_uuid[1].encode('utf-8')).hexdigest()
        except Exception as e:
            gv.logger.error(e)
        return identifier
