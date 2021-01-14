from sourceRank.SourceRank import SourceRank
from sourceRank.helper.utils import (compute_importance_from_exponential_distribution)
from helper.settings import (logger, art_es_index,
                             score_art_es_index, person_es_index,
                             org_es_index, org_es_index_features,
                             default_name, score_key, auth_es_index_features,
                             http_response_200, http_response_500,
                             fusion_score_server, fusion_score_port,
                             fusion_score_endpoint)
from helper.utils import normalize_value, relevance_mapping
from helper.streaming_thread import ThreadsProcessor
from fandango_models.source_credibility_models import TrustworthinessDoc, PublisherFeaturesDoc, AuthorFeatureDoc
from connectors.elasticsearch_connector import ElasticsearchConnector
from elasticsearch_dsl.response import Response
import numpy as np
import itertools
import requests


class FDGSourceCredibility(object):

    def process_analysis(self, publishers: list, authors: list, article_uuid: str,
                         article_url: str, elasticsearch_connector: ElasticsearchConnector,
                         source_rank: SourceRank):
        try:
            # 1. Perform analysis
            response: dict = self.perform_source_credibility_analysis(
                publishers=publishers,
                authors=authors,
                article_url=article_url,
                elasticsearch_connector=elasticsearch_connector,
                source_rank=source_rank)

            if response.get("code") == 200:
                # 2. Call Fusion Score
                logger.info("Calling Fusion Score Service")
                ThreadsProcessor.start_new_streaming_process(
                    thread_name="fusion_score",
                    target_func=self.update_fusion_score,
                    params=(fusion_score_server, fusion_score_port,
                            fusion_score_endpoint, article_uuid,))
                """response_fusion_score: dict = self.update_fusion_score(
                    server=fusion_score_server,
                    port=fusion_score_port,
                    endpoint=fusion_score_endpoint,
                    article_uuid=article_uuid)"""
        except Exception as e:
            logger.error(e)

    def perform_source_credibility_analysis(self, publishers: list, authors: list, article_url: str,
                                            elasticsearch_connector: ElasticsearchConnector,
                                            source_rank: SourceRank) -> dict:
        response: dict = {"message": http_response_500, "code": 500}
        try:
            # ====================================================================
            # Publisher Analysis
            # ====================================================================
            output_pub_trustworthiness: TrustworthinessDoc = TrustworthinessDoc(
                trustworthiness=normalize_value(),
                relevance=normalize_value(mu=0.1,
                                          sigma=0.05))
            for publisher in publishers:
                logger.info(f"Analysing Publisher {publisher.get('identifier')}")

                # 1. Check if the publisher contains data
                non_exist: bool = elasticsearch_connector.check_document_in_index_by_id(
                    index=org_es_index_features, uuid=publisher.get("identifier"))

                if non_exist:
                    analyse_static: bool = True
                else:
                    analyse_static: bool = False

                # 4. Compute publisher features
                publisher_features: PublisherFeaturesDoc = self.get_publisher_features(
                    elasticsearch_connector=elasticsearch_connector,
                    source_rank=source_rank, publisher=publisher,
                    article_url=article_url,
                    analyse_static=analyse_static)
                
                # 5. Update features in Elasticsearch
                if analyse_static:
                    elasticsearch_connector.bulk_data_into_index(
                        index=org_es_index_features,
                        uuid=publisher.get("identifier"),
                        source_data=publisher_features.__dict__)
                else:
                    # Update only non-static features
                    params = {"text_rank_analysis": publisher_features.text_rank_analysis,
                              "anonymous_rank_analysis": publisher_features.anonymous_rank_analysis,
                              "last_updated": publisher_features.last_updated}
                    body = {"doc": params}
                    elasticsearch_connector.update_fields_to_index(
                        index=org_es_index_features,
                        uuid=publisher.get("identifier"),
                        body=body)

                # 6. Compute Trustworthiness & relevance
                publisher_features_dict = {"open_rank": publisher_features.open_rank_analysis.get("rank"),
                                           "suffix_rank": publisher_features.suffix_rank_analysis.get("rank"),
                                           "category_rank": publisher_features.category_rank_analysis.get("rank"),
                                           "twitter_rank": publisher_features.twitter_rank_analysis.get("rank"),
                                           "whois_rank": publisher_features.whois_rank_analysis.get("rank"),
                                           "text_rank": publisher_features.text_rank_analysis.get("rank"),
                                           "anonymous_rank": publisher_features.anonymous_rank_analysis.get("rank")}
                output_pub_trustworthiness: TrustworthinessDoc = self.get_trustworthiness_from_features(
                    features=publisher_features_dict,
                    metrics=self.get_publisher_metrics_importances(),
                    total_articles=publisher_features.text_rank_analysis.get("total_articles"))

                # 7. Update only non-static features
                params = {score_key: 100*output_pub_trustworthiness.trustworthiness,
                          "relevance": output_pub_trustworthiness.relevance,
                          "status": "done"}
                body = {"doc": params}
                elasticsearch_connector.update_fields_to_index(
                    index=org_es_index,
                    uuid=publisher.get("identifier"),
                    body=body)

            # ====================================================================
            # Author Analysis
            # ====================================================================
            publisher_rank_analysis: dict = {"rank": output_pub_trustworthiness.trustworthiness,
                                             "relevance": output_pub_trustworthiness.relevance}
            for author in authors:
                logger.info(f"Analysing Author {author.get('identifier')}")

                # 1. Compute author features
                author_features: AuthorFeatureDoc = self.get_author_features(
                    elasticsearch_connector=elasticsearch_connector,
                    author=author, publisher_rank_analysis=publisher_rank_analysis)

                # 2. Compute Trustworthiness & relevance
                author_features_dict = {"text_rank": author_features.text_rank_analysis.get("rank"),
                                        "publisher_rank": publisher_rank_analysis.get("rank")}
                output_aut_trustworthiness: TrustworthinessDoc = self.get_trustworthiness_from_features(
                    features=author_features_dict, metrics=self.get_author_metrics_importances(),
                    total_articles=author_features.text_rank_analysis.get("total_articles"))

                # 3. Verify if author exists in fdg-person-features
                non_exist_auth: bool = elasticsearch_connector.check_document_in_index_by_id(
                    index=auth_es_index_features, uuid=author.get("identifier"))

                if non_exist_auth:
                    # Generate entry
                    elasticsearch_connector.bulk_data_into_index(
                        index=auth_es_index_features,
                        uuid=author.get("identifier"),
                        source_data=author_features.__dict__)
                else:
                    # Update features in Elasticsearch
                    body = {"doc": author_features.__dict__}
                    elasticsearch_connector.update_fields_to_index(
                        index=auth_es_index_features,
                        uuid=author.get("identifier"),
                        body=body)
                # 4. Update scores in Elasticsearch fdg-ap-person-features
                params = {score_key: 100*output_aut_trustworthiness.trustworthiness,
                          "relevance": output_aut_trustworthiness.relevance,
                          "status": "done"}
                body = {"doc": params}
                elasticsearch_connector.update_fields_to_index(
                    index=person_es_index,
                    uuid=author.get("identifier"),
                    body=body)
            response["message"]: str = http_response_200
            response["code"]: int = 200
        except Exception as e:
            logger.error(e)
        return response

    def get_publisher_features(self, elasticsearch_connector: ElasticsearchConnector,
                               source_rank: SourceRank, publisher: dict,
                               article_url: str, analyse_static: bool) -> PublisherFeaturesDoc:
        publisher_features: PublisherFeaturesDoc = object.__new__(PublisherFeaturesDoc)
        try:
            # Compute analysis

            # Parser URL
            url: str = publisher.get("source_data").get("url")
            # country: str = publisher.get("source_data").get("country")
            # country_code: Optional[str] = None
            uuid: str = publisher.get("identifier")
            field: str = "publisher"

            res_parser = source_rank.process_url(url=url)

            # Only updated if necessary
            if analyse_static:
                # 1. Open Rank Analysis
                domain: str = res_parser.registered_domain
                fqdn: str = res_parser.fqdn
                res_open_rank: dict = source_rank.get_open_rank_analysis(domain=domain).__dict__

                # 2. Suffix Analysis
                res_suffix: dict = source_rank.get_suffix_analysis(suffix=res_parser.suffix).__dict__

                # 3. WHOIS Analysis
                res_whois: dict = source_rank.get_whois_analysis(domain=domain).__dict__

                # 4. Category Analysis
                res_category: dict = source_rank.get_category_analysis(
                    url=fqdn).__dict__

                # 5. Retrieve Twitter info from URL
                res_twitter: dict = source_rank.get_twitter_analysis(
                    url=article_url).__dict__
            else:
                # 1. Retrieve data from ES
                res_org: dict = elasticsearch_connector.retrieve_data_from_index_by_id(
                    index=org_es_index_features,
                    uuid=uuid)
                res_open_rank: dict = res_org.get("open_rank_analysis")
                res_suffix: dict = res_org.get("suffix_rank_analysis")
                res_whois: dict = res_org.get("whois_rank_analysis")
                res_category: dict = res_org.get("category_rank_analysis")
                res_twitter: dict = res_org.get("twitter_rank_analysis")

            # 6. Text rank
            res_text_rank: dict = self.get_text_rank(
                elasticsearch_connector=elasticsearch_connector,
                query=uuid, field=field,
                es_art_index=art_es_index,
                es_score_index=score_art_es_index)

            # 7. Anonymous rank
            res_anonymous_rank: dict = self.get_anonymous_rank(
                elasticsearch_connector=elasticsearch_connector,
                index=art_es_index,
                authors_index=person_es_index,
                field=field,
                query=uuid,
                anonymous_key=default_name)

            # 8. Generate Output
            publisher_features: PublisherFeaturesDoc = PublisherFeaturesDoc(
                open_rank_analysis=res_open_rank,
                suffix_rank_analysis=res_suffix,
                whois_rank_analysis=res_whois,
                category_rank_analysis=res_category,
                twitter_rank_analysis=res_twitter,
                anonymous_rank_analysis=res_anonymous_rank,
                text_rank_analysis=res_text_rank)

        except Exception as e:
            logger.error(e)
        return publisher_features

    def get_author_features(self, elasticsearch_connector: ElasticsearchConnector,
                            author: dict, publisher_rank_analysis: dict) -> AuthorFeatureDoc:
        author_features: AuthorFeatureDoc = object.__new__(AuthorFeatureDoc)
        try:
            uuid: str = author.get("identifier")
            field: str = "authors"

            # 6. Text rank
            res_text_rank: dict = self.get_text_rank(
                elasticsearch_connector=elasticsearch_connector,
                query=uuid, field=field,
                es_art_index=art_es_index,
                es_score_index=score_art_es_index)
            author_features: AuthorFeatureDoc = AuthorFeatureDoc(
                publisher_rank_analysis=publisher_rank_analysis,
                text_rank_analysis=res_text_rank)
        except Exception as e:
            logger.error(e)
        return author_features

    @staticmethod
    def get_trustworthiness_from_features(features: dict, metrics: dict, total_articles: int) -> TrustworthinessDoc:
        output_trustworthiness: TrustworthinessDoc = TrustworthinessDoc(
            trustworthiness=normalize_value(), relevance=normalize_value(
                mu=0.1, sigma=0.05))
        try:
            # =====================================================
            # Compute Final trustworthiness
            # =====================================================

            trustworthiness: float = 0.0
            weights_sum: float = 0.0
            for metric, importance in metrics.items():
                # 1. Retrieve values
                rank_value: float = features.get(metric, 0.0)
                importance_value: float = compute_importance_from_exponential_distribution(
                    x=importance)

                # 2. Update score
                trustworthiness += rank_value*importance_value
                weights_sum += importance_value

            # 3. Relevance
            relevance: float = relevance_mapping(x=total_articles)
            if relevance == 0:
                relevance = normalize_value(
                    mu=0.1, sigma=0.05)

            output_trustworthiness.trustworthiness: float = round(trustworthiness/weights_sum, 3)
            output_trustworthiness.relevance: float = round(relevance, 3)
            output_trustworthiness.analysed: bool = True
            output_trustworthiness.error: bool = False
        except Exception as e:
            logger.error(e)
        return output_trustworthiness

    @staticmethod
    def get_publisher_metrics_importances() -> dict:
        metrics_importances: dict = {"open_rank": 5, "whois_rank": 5,
                                     "suffix_rank": 2, "category_rank": 4,
                                     "twitter_rank": 4.5, "text_rank": 1,
                                     "anonymous_rank": 1}
        return metrics_importances

    @staticmethod
    def get_author_metrics_importances() -> dict:
        metrics_importances: dict = {"publisher_rank": 5, "text_rank": 2}
        return metrics_importances
    
    @staticmethod
    def get_text_rank(elasticsearch_connector: ElasticsearchConnector, query: str,
                      field: str, es_art_index: str, es_score_index) -> dict:
        text_rank_analysis: dict = {"rank": 0.0, "total_articles": 0}
        try:
            # 1. Retrieve all articles associated to the entity
            response: Response = elasticsearch_connector.search_data_from_elasticsearch_by_matching(
                index=es_art_index, fields=[field], query=query)

            response_dct: dict = response.to_dict()
            text_rank: float = normalize_value(mu=0.1, sigma=0.05)
            total_articles: int = 0
            if response_dct.get("hits").get("total").get("value") > 0:
                articles_uuids: list = [i.get("_id") for i in response_dct.get("hits").get("hits")]
                total_articles: int = len(articles_uuids)

                # 2. For each article id, retrieve score if available
                response_articles: Response = elasticsearch_connector.filter_data_from_index_by_uuid(
                    index=es_score_index, uuids=articles_uuids)
                response_articles_dct: dict = response_articles.to_dict()

                if response_articles_dct.get("hits").get("total").get("value") > 0:
                    text_scores: list = [np.multiply(i.get("_source").get("textScore"),
                                                     i.get("_source").get("relevance"))
                                         for i in response_articles_dct.get("hits").get("hits")]
                    # 3. Compute weighted mean
                    text_rank: float = round(float(sum(text_scores)/len(text_scores)),
                                             3)
            text_rank_analysis["rank"]: float = text_rank
            text_rank_analysis["total_articles"]: int = total_articles
        except Exception as e:
            logger.error(e)
        return text_rank_analysis

    @staticmethod
    def get_anonymous_rank(elasticsearch_connector: ElasticsearchConnector, index: str,
                           authors_index: str, field: str, query: str, anonymous_key: str) -> dict:
        anonymous_rank_analysis: dict = {"rank": 0.0, "total_authors": 0}
        try:
            # 1. Retrieve all articles associated to the entity
            response: Response = elasticsearch_connector.search_data_from_elasticsearch_by_matching(
                index=index, fields=[field], query=query)
            response_dct: dict = response.to_dict()
            if response_dct.get("hits").get("total").get("value") > 0:

                # 2. Count authors
                authors: list = [i.get("_source").get("authors")
                                 for i in response_dct.get("hits").get("hits")]
                authors_uuids: list = list(set(itertools.chain.from_iterable(authors)))
                total_authors: int = len(authors_uuids)
                total_anonymous: int = 0

                # 3. Count how many of them are anonymous
                response_authors: Response = elasticsearch_connector.filter_data_from_index_by_uuid(
                    index=authors_index, uuids=authors_uuids)
                response_authors_dct: dict = response_authors.to_dict()

                if response_authors_dct.get("hits").get("total").get("value") > 0:
                    total_anonymous: int = len(
                        [i for i in response_authors_dct.get("hits").get("hits")
                         if i.get("_source").get("name") == anonymous_key])

                anonymous_rank: float = round(1 - (total_anonymous/total_authors), 3)
                anonymous_rank_analysis["rank"]: float = anonymous_rank
                anonymous_rank_analysis["total_authors"]: int = total_authors
            else:
                anonymous_rank_analysis["rank"]: float = normalize_value(
                    mu=0.1, sigma=0.05)

        except Exception as e:
            logger.error(e)
        return anonymous_rank_analysis

    @staticmethod
    def update_fusion_score(server: str, port: str, endpoint: str, article_uuid: str) -> dict:
        response: dict = {"status": 500, "message": http_response_500}
        try:
            url: str = f"http://{server}:{port}/{endpoint}"
            data: dict = {"identifier": article_uuid}
            response_api = requests.post(url=url, json=data, timeout=30)
            response["status"]: int = response_api.status_code
            if response_api.status_code == 200:
                response["message"]: str = http_response_200
        except Exception as e:
            logger.error(e)
        return response