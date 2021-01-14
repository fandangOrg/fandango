from helper.settings import logger
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch.helpers import bulk
from fuzzywuzzy import fuzz
import hashlib
from typing import Optional
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.response import Response


class ElasticsearchConnector:
    def __init__(self, host: str, port: str):
        self.host: str = host
        self.port: str = port
        self.es: Optional[Elasticsearch] = None
        self.connection: bool = False

    def connect(self):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port}],
                                    timeout=1000)
            if self.es.ping(request_timeout=1):
                self.connection: bool = True
                logger.info('Connected to ElasticSearch at \'%s:%s\'.', self.host, self.port)
            else:
                self.connection: bool = False
                logger.info('It was not possible to connect to \'%s:%s\'.', self.host, self.port)
        except Exception as e:
            logger.error(e)
        return self

    def get_indexes(self) -> list:
        return list(self.es.indices.get_alias("*").keys())

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
            logger.error(e)
        return items

    def retrieve_data_from_index_by_id(self, index, uuid) -> dict:
        response: dict = {}
        try:
            results = self.es.get(index=index, id=uuid)
            # Check results from generator
            response: dict = results.get('_source', {})
        except Exception as e:
            pass
        return response

    def check_document_in_index_by_id(self, index: str, uuid: str) -> bool:
        not_exist: bool = True
        try:
            results: dict = self.es.get(index=index, id=uuid)

            # Check results from generator
            response = results.get('_source', {})
            if response:
                not_exist: bool = False
        except Exception as e:
            pass
        return not_exist

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
            logger.error(e)
        return response

    def bulk_data_into_index(self, index: str, uuid: str, source_data: dict) -> dict:
        response: dict = {}
        try:
            actions = [{'_index': index,
                        '_id': uuid,
                        '_source': source_data}]
            res: dict = bulk(self.es, actions, refresh='wait_for')
            if res:
                response = self.retrieve_data_from_index_by_id(index=index, uuid=uuid)
        except Exception as e:
            logger.error(e)
        return response

    def update_fields_to_index(self, index: str, uuid: str, body: dict):
        try:
            self.es.update(index=index, id=uuid, body=body)
        except Exception as e:
            logger.error(e)

    def create_new_index(self, index, body=None):
        res = True
        try:
            if not self.es.indices.exists(index=index):
                # Simple index creation with no particular mapping
                if body is None:
                    body = {}
                self.es.indices.create(index=index, body=body)
        except Exception as e:
            logger.error(e)
            res = False
        return res

    def remove_index(self, index):
        res = True
        try:
            logger.info('Removing index %s from Elasticsearch', str(index))
            self.es.indices.delete(index=index, ignore=[400, 404])
        except Exception as e:
            logger.error(e)
            res = False
        return res

    @staticmethod
    def generate_64_uuid_from_string(data_uuid: str) -> str:
        identifier: str = ""
        try:
            identifier: str = hashlib.sha256(data_uuid.lower().encode('utf-8')).hexdigest()
        except Exception as e:
            print(e)
        return identifier

    @staticmethod
    def generate_128_uuid_from_string(data_uuid: str) -> str:
        identifier: str = ""
        try:
            identifier: str = hashlib.sha512(data_uuid.lower().encode('utf-8')).hexdigest()
        except Exception as e:
            print(e)
        return identifier

    def search_data_from_elasticsearch_by_matching(self, index: str, fields: list, query) -> Response:
        response: Response = object.__new__(Response)
        try:
            multi_match = MultiMatch(query=query, fields=fields)

            search_query: Search = Search(using=self.es, index=index).query(multi_match)
            response: Response = search_query.execute()

        except Exception as e:
            logger.error(e)
        return response

    def filter_data_from_index_by_uuid(self, index: str, uuids: list):
        response: Response = object.__new__(Response)
        try:
            search_query: Search = Search(using=self.es, index=index) \
                .filter("terms", _id=uuids)

            response: Response = search_query.execute()
        except Exception as e:
            logger.error(e)
        return response