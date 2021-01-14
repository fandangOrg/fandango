from connectors.elasticsearch_connector import ElasticsearchConnector
from sourceRank.SourceRank import SourceRank
from helper.settings import (logger, open_rank_api_key, whois_api_key, news_api_key,
                             access_token_secret, access_token, consumer_secret,
                             consumer_key, botometer_api_key, http_response_500,
                             http_response_200, person_es_index, org_es_index)
from fandango_models.article import Article
from fandango_models.publisher import Publisher
from fandango_models.author import Author
from fandango_models.source_credibility_models import GraphAnalyzerOutputDoc, AnalysisDoc
from helper.utils import remove_non_alphabetical_symbols
# from helper.streaming_thread import ThreadsProcessor
from analysis.fandango_source_credibility import FDGSourceCredibility


class SourceCredibilityConnector(object):
    def __init__(self, elasticsearch_connector: ElasticsearchConnector):
        self.elasticsearch_connector: ElasticsearchConnector = elasticsearch_connector
        self.source_rank: SourceRank = SourceRank(
            open_rank_api_key=open_rank_api_key,
            whois_api_key=whois_api_key,
            news_api_key=news_api_key,
            access_token_secret=access_token_secret,
            access_token=access_token,
            consumer_secret=consumer_secret,
            consumer_key=consumer_key,
            botometer_api_key=botometer_api_key)
        self.fandango_analyser: FDGSourceCredibility = FDGSourceCredibility()
        self.person_es_index: str = person_es_index
        self.org_es_index: str = org_es_index

    def extract_authors_from_document(self, document: Article, es_index: str) -> list:
        authors_data: list = []
        try:
            domain_info = self.source_rank.process_url(url=document.url)
            source_domain = domain_info.domain

            # 1. For each author
            for aut_name in document.authors:
                # Considering Name + source_domain
                aut_name_filtered: str = remove_non_alphabetical_symbols(aut_name)
                data_uuid: str = aut_name_filtered.replace(" ", "") + source_domain
                uuid_aut = self.elasticsearch_connector.generate_128_uuid_from_string(
                    data_uuid=data_uuid)

                # Check if the author is already in Elasticsearch by uuid
                response = self.elasticsearch_connector.retrieve_data_from_index_by_id(
                    index=es_index,
                    uuid=uuid_aut)
                source_data = response
                # If it does not exist yet
                if not response:
                    author_obj: Author = Author(
                        identifier=uuid_aut, name=aut_name,
                        affiliation=document.publisher,
                        url=document.url)
                    source_data = author_obj.build_output()

                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(
                        index=es_index,
                        uuid=uuid_aut,
                        source_data=source_data)
                # Append data to response
                authors_data.append({"identifier": uuid_aut, "source_data": source_data})

        except Exception as e:
            logger.error(e)
        return authors_data

    def extract_publisher_from_document(self, document, es_index: str) -> list:
        publisher_data: list = []
        try:
            if not isinstance(document.publisher, list):
                document.publisher = [document.publisher]

            for pub_name in document.publisher:
                domain_info = self.source_rank.process_url(url=document.url)
                source_domain: str = domain_info.domain
                data_uuid: str = source_domain

                # Check if the publisher is already in Elasticsearch by uuid
                uuid_pub = self.elasticsearch_connector.generate_128_uuid_from_string(
                    data_uuid=data_uuid)
                response: dict = self.elasticsearch_connector.retrieve_data_from_index_by_id(
                    index=es_index,
                    uuid=uuid_pub)

                source_data: dict = response
                # If it does not exist yet
                if not response:
                    pub_obj: Publisher = Publisher(
                        identifier=uuid_pub, name=pub_name,
                        url=document.sourceDomain,
                        country=document.country,
                        nationality=document.nationality)

                    source_data: dict = pub_obj.build_output()

                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(index=es_index,
                                                                                 uuid=uuid_pub,
                                                                                 source_data=source_data)
                # Append data to response
                publisher_data.append({"identifier": uuid_pub, "source_data": source_data})
        except Exception as e:
            logger.error(e)
        return publisher_data

    def apply_analysis(self, document: Article) -> GraphAnalyzerOutputDoc:
        response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
            message=http_response_500,
            status=500,
            data=AnalysisDoc().__dict__)
        try:
            # 1. Extract Authors from document
            authors_data: list = self.extract_authors_from_document(
                document=document,
                es_index=self.person_es_index)

            # 2. Extract Publisher
            publisher_data: list = self.extract_publisher_from_document(
                document=document, es_index=self.org_es_index)

            # 3. Compute analysis
            # Add Thread
            """ThreadsProcessor.start_new_streaming_process(
                thread_name="offline",
                target_func=self.fandango_analyser.process_analysis,
                params=(publisher_data, authors_data,
                        document.identifier, document.url,
                        self.elasticsearch_connector,
                        self.source_rank, ))"""

            response_analysis: dict = self.fandango_analyser.process_analysis(
                publishers=publisher_data,
                authors=authors_data,
                article_uuid=document.identifier,
                article_url=document.url,
                elasticsearch_connector=self.elasticsearch_connector,
                source_rank=self.source_rank)

            # 4. Generate analysis response
            output_analysis: AnalysisDoc = self.build_source_credibility_response(
                identifier=document.identifier,
                authors_data=authors_data,
                publisher_data=publisher_data)

            # 5. Generate service response
            response: GraphAnalyzerOutputDoc = GraphAnalyzerOutputDoc(
                message=http_response_200,
                status=200,
                data=output_analysis.__dict__)

        except Exception as e:
            logger.error(e)
        return response

    @staticmethod
    def build_source_credibility_response(identifier: str, authors_data: list,
                                          publisher_data: list) -> AnalysisDoc:
        response: AnalysisDoc = AnalysisDoc()
        try:
            authors_uuids: list = [aut.get("identifier") for aut in authors_data]
            publisher_uuids: list = [pub.get("identifier") for pub in publisher_data]
            response: AnalysisDoc = AnalysisDoc(
                identifier=identifier,
                authors=authors_uuids,
                publisher=publisher_uuids)
        except Exception as e:
            logger.error(e)
        return response

    def update_analysis_into_elasticsearch(self, data_to_update: dict, keys: list):
        try:
            for k in keys:
                n_elements: int = len(data_to_update[k]["uuids"])
                for i in range(n_elements):
                    uuid: str = data_to_update[k]["uuids"][i]
                    trustworthiness: float = data_to_update[k]["scores"][i]
                    status: int = data_to_update[k]["status"][i]
                    index: str = data_to_update[k]["index"][i]

                    params = {"trustworthiness": trustworthiness, "status": status}
                    body = {"doc": params}
                    self.elasticsearch_connector.update_fields_to_index(index=index, uuid=uuid,
                                                                        body=body)
        except Exception as e:
            logger.error(e)