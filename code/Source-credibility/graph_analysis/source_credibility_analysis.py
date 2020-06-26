import os
import numpy as np
import pandas as pd
from typing import Optional
from helper import global_variables as gv
from scipy import stats
from tweepy import API
from models.graph_models import Neo4jInputDoc, Neo4jOutputDoc, SourceCredibilityOutputDoc
from managers.neo4j_queries import Neo4jQueries
from managers.neo4j_connector import NEO4JConnector
from managers.elasticsearch_connector import ElasticsearchManager
from helper.helper import (normalize_trustworthiness, normalize_value,
                           merge_dataframes,
                           change_importance, get_current_timestamp)
from py2neo import Graph
from graph_analysis.social_analysis_metrics import (compute_openrank_score, compute_twitter_score,
                                                    compute_suffix_score,connect_twitter,
                                                    compute_text_score, get_publisher_score,
                                                    compute_media_type_score, generate_twitter_scorer,
                                                    compute_article_rank, retrieve_authors_associated_to_publisher,
                                                    collect_domain_info_from_db, get_data_from_neo4j,
                                                    get_user_by_username, get_user_data, check_twitter_analysis_date)


class SourceCredibility:
    def __init__(self, neo4j_connector: NEO4JConnector,
                 es_connector: ElasticsearchManager = None):
        self.neo4j_connector: NEO4JConnector = neo4j_connector
        self.neo4j_queries_manager: Neo4jQueries = Neo4jQueries()
        self.es_connector: ElasticsearchManager = es_connector
        self.sheet_names_tld: list = gv.sheet_names_tld
        self.score_name: str = gv.score_name
        self.filepath_tld: str = os.path.join(gv.resources_dir, gv.filepath_tld)
        self.art_index: str = gv.art_es_index
        self.media_type_csv: str = os.path.join(gv.resources_dir, gv.csv_filepath)
        self.twitter_api: Optional[API] = None
        self.twitter_score_func = None

    def set_up_twitter_connection(self):
        try:
            self.twitter_api: API = connect_twitter()
        except Exception as e:
            gv.logger.error(e)

    def set_up_twitter_score_function(self, minval: int = 0, maxval: int = 100):
        try:
            self.twitter_score_func = generate_twitter_scorer(
                minval=minval, maxval=maxval)
        except Exception as e:
            gv.logger.error(e)

    def start_analysis(self, document: Neo4jInputDoc):
        response: SourceCredibilityOutputDoc = SourceCredibilityOutputDoc(
            message=gv.http_response_500, status=500)
        try:
            # 1. Generate DataFrames from the input document
            response_tables: Neo4jOutputDoc = self.neo4j_connector.create_tables_from_dict(
                data=document)

            if response_tables.status == 200:
                # 2. Build graph
                response_build: Neo4jOutputDoc = self.neo4j_connector.build_graph(
                    data_tables=response_tables.data)

                if response_build.status == 200:
                    # 3) Apply analysis and generate output
                    response_analysis: SourceCredibilityOutputDoc = self.analyse_trustworthiness(
                        data_tables=response_tables.data)

                    response.message: str = response_analysis.message
                    response.status: int = response_analysis.status
                    response.data: dict = response_analysis.data

        except Exception as e:
            gv.logger.error(e)
        return response

    def analyse_trustworthiness(self, data_tables: dict):
        response: SourceCredibilityOutputDoc = SourceCredibilityOutputDoc(
            message=gv.http_response_500,
            status=500)
        try:
            # 1. Retrieve data
            publisher_df = data_tables["publisher_table"]
            authors_df = data_tables["authors_table"]

            # 2. Compute Publisher Trustworthiness
            publisher_df[self.score_name], publisher_df["relevance"] = publisher_df.apply(
                self.compute_trustworthiness, args=(self.neo4j_connector.graph,
                                                    "publisher"),
                axis=1, result_type='expand').T.values

            # 3. Retrieve ALL authors associated to the publisher
            author_cols: list = list(authors_df.columns)
            remain_authors: list = self.retrieve_all_authors_from_publisher(
                self.neo4j_connector.graph,
                label_a=self.neo4j_queries_manager.author_node_label,
                label_b=self.neo4j_queries_manager.publisher_node_label,
                relationship=self.neo4j_queries_manager.author_publisher_relationship,
                publisher_uuid=publisher_df["identifier"].values[
                 0],
                authors_done=authors_df["identifier"].values.tolist(),
                columns=author_cols)

            total_authors_df: pd.DataFrame = merge_dataframes(remain_authors, authors_df)

            # 4. Compute Author Trustworthiness
            total_authors_df[self.score_name], total_authors_df["relevance"] = total_authors_df.apply(
                self.compute_trustworthiness, args=(self.neo4j_connector.graph,
                                                    "author"),
                axis=1, result_type='expand').T.values

            # 5.Generate output
            # 5.1 Authors
            response_data: dict = {}
            output_authors: dict = self.prepare_response(
                data_df=total_authors_df,
                index=self.neo4j_connector.person_index,
                main_key="authors",
                score_name=self.score_name)
            response_data.update(output_authors)

            # 5.2 Publisher
            output_publisher: dict = self.prepare_response(
                data_df=publisher_df,
                index=self.neo4j_connector.publisher_index,
                main_key="publisher",
                score_name=self.score_name)
            response_data.update(output_publisher)

            # 6. Generate final response
            response.message: str = gv.http_response_200
            response.status: int = 200
            response.data: dict = response_data

        except Exception as e:
            gv.logger.error(e)
        return response

    @staticmethod
    def prepare_response(data_df: pd.DataFrame, index: str, main_key: str, score_name: str):
        output = {main_key: {}}
        try:
            data_df_to_dict: dict = data_df.to_dict()
            uuids = list(data_df_to_dict["identifier"].values())
            output[main_key]["uuids"] = uuids

            scores = list(data_df_to_dict[score_name].values())
            output[main_key]["scores"] = scores

            status = ["done" for i in range(len(uuids))]
            output[main_key]["status"] = status

            es_index = [index for i in range(len(uuids))]
            output[main_key]["index"] = es_index

            relevance = list(data_df_to_dict["relevance"].values())
            output[main_key]["relevance"] = relevance
        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def preprocess_data(data: Optional[pd.DataFrame]):
        data_dct: dict = {"processed_timestamp": get_current_timestamp(),
                          "status": gv.status_failed}
        try:
            # Convert to dict
            data_dct: dict = data.to_dict()

            # Add status
            data_dct["status"]: int = gv.status_in_progress

        except Exception as e:
            gv.logger.error(e)
        return data_dct

    @staticmethod
    def retrieve_all_authors_from_publisher(graph: Graph, label_a: str, label_b: str,
                                            relationship:str, publisher_uuid: str,
                                            authors_done: list = None, columns: list = None):
        remain_authors: list = []
        try:
            remain_authors: list = retrieve_authors_associated_to_publisher(
                graph, label_a, label_b, relationship,
                publisher_uuid, authors_done=authors_done,
                columns=columns)
        except Exception as e:
            gv.logger.error(e)
        return remain_authors

    def compute_relevance(self, uuid: str, graph: Graph, entity: str):
        relevance: int = 0
        try:
            # Publisher Relevance
            if entity == self.neo4j_queries_manager.publisher_node_label.lower():
                # Compute RELEVANCE
                relevance: int = compute_article_rank(
                    graph, label_a=self.neo4j_queries_manager.article_node_label,
                    label_b=self.neo4j_queries_manager.publisher_node_label,
                    uuid=uuid,
                    relationship=self.neo4j_queries_manager.get_article_publisher_relationship(),
                    uuid_label="identifier")
            # Author Relevance
            else:
                relevance: int = compute_article_rank(
                    graph, label_a=self.neo4j_queries_manager.article_node_label,
                    label_b=self.neo4j_queries_manager.author_node_label,
                    uuid=uuid,
                    relationship=self.neo4j_queries_manager.get_article_author_relationship(),
                    uuid_label="identifier")

        except Exception as e:
            gv.logger.error(e)
        return relevance

    def compute_trustworthiness(self, data: Optional[pd.Series], graph: Graph,
                                entity: str, update_neo4j: bool = True):
        trustworthiness: float = normalize_value()
        relevance: int = 0
        response: tuple = (trustworthiness, relevance)

        try:
            # 1. Pre-process data
            data: dict = self.preprocess_data(data)
            response_twitter: dict = {}
            # 2. Perform Analysis

            # 2.1 Publisher Analysis
            if entity == self.neo4j_queries_manager.publisher_node_label.lower():
                if self.twitter_api is None:
                    self.set_up_twitter_connection()
                if self.twitter_score_func is None:
                    self.set_up_twitter_score_function()

                # 2.1 Twitter response
                response_twitter: dict = self.analyse_twitter_account(
                    graph,
                    label=self.neo4j_queries_manager.publisher_node_label,
                    property_label="identifier",
                    property=data["identifier"])
                # 2.2 Get scores
                scores_data, non_importances = self.get_scores_importances_from_publisher(
                    graph, data, response_twitter)

            # 2.2 Author Analysis
            else:
                scores_data, non_importances = self.get_scores_importances_from_author(
                    graph, data)
                response_twitter["analyse"] = False

            # 3. Update Neo4j properties
            if update_neo4j:
                self.update_properties_in_graph(graph, entity,
                                                uuid=data["identifier"], data=scores_data)

            # Get score values and retrieve non-normalize trustworthiness
            scores = self.get_scores_values(scores_data)
            importances = self.normalize_importances(non_importances)
            gv.logger.info("Computing Trustworthiness!")
            non_trustworthiness: float = self.calculate_multimodal_score(scores, importances)

            # Normalize trustworthiness
            trustworthiness: float = normalize_trustworthiness(non_trustworthiness)
            relevance: int = self.compute_relevance(data["identifier"], graph, entity)

            # Update property in Neo4j
            if update_neo4j:
                final_data = {"trustworthiness": trustworthiness,
                              "status": data["status"],
                              "relevance": relevance}
                if entity == self.neo4j_queries_manager.publisher_node_label.lower() and response_twitter["analyse"]:
                    final_data.update({"processed_timestamp": data["processed_timestamp"]})
                self.update_properties_in_graph(graph, entity, uuid=data["identifier"],
                                                data=final_data)
            # ==========================================================================================================
            gv.logger.info("Done!")
            response: tuple = (trustworthiness, relevance)
        except Exception as e:
            gv.logger.error(e)
        return response

    def compute_author_scores(self, graph: Graph, data: dict):
        scores: dict = {}
        try:
            article_rank = compute_article_rank(
                graph, label_a=self.neo4j_queries_manager.article_node_label,
                label_b=self.neo4j_queries_manager.author_node_label,
                uuid=data["identifier"],
                relationship=self.neo4j_queries_manager.get_article_author_relationship(),
                uuid_label="identifier")

            # 1) Text Rank
            gv.logger.info("Computing Text Rank for Authors!")
            text_score = compute_text_score(self.es_connector, graph, uuid=data["identifier"],
                                            label_a=self.neo4j_queries_manager.article_node_label,
                                            label_b=self.neo4j_queries_manager.author_node_label,
                                            relationship=self.neo4j_queries_manager.article_author_relationship,
                                            art_index=self.art_index, relevance=article_rank)
            scores.update({"text_rank": text_score})

            # 2) Publisher Rank
            gv.logger.info("Computing Publisher Rank for Authors!")
            publisher_score = get_publisher_score(
                graph, uuid=data["identifier"],
                label_a=self.neo4j_queries_manager.author_node_label,
                label_b=self.neo4j_queries_manager.publisher_node_label,
                relationship=self.neo4j_queries_manager.author_publisher_relationship)

            scores.update({"publisher_rank": publisher_score})
        except Exception as e:
            gv.logger.error(e)
        return scores

    @staticmethod
    def analyse_twitter_account(graph: Graph, label: str, property_label: str, property: str):
        return check_twitter_analysis_date(graph, label, property_label, property)

    def compute_publisher_scores(self, graph: Graph, data: dict, response_twitter: dict):
        scores: dict = {}
        try:
            # 1. Open Page Rank
            gv.logger.info("Computing Open Page Rank!")
            pagerank_score = compute_openrank_score(
                data["url"], label="page_rank_decimal")
            scores.update({"page_rank": pagerank_score})

            # 2. Twitter Rank
            gv.logger.info("Computing Twitter Rank!")
            if response_twitter["analyse"]:
                twitter_score = compute_twitter_score(
                    self.twitter_api, data["name"], self.twitter_score_func)
            else:
                twitter_score = response_twitter["score"]

            scores.update({"twitter_rank": twitter_score})

            # 3. Suffix Rank
            gv.logger.info("Computing Suffix Rank!")
            suffix_score = compute_suffix_score(data["url"], sheet_names=self.sheet_names_tld,
                                                filepath=self.filepath_tld,
                                                key="importance_weight")
            scores.update({"suffix_rank": suffix_score["importance_weight"]})

            # 4. Centrality rank
            article_rank = compute_article_rank(
                graph, label_a=self.neo4j_queries_manager.article_node_label,
                label_b=self.neo4j_queries_manager.publisher_node_label,
                uuid=data["identifier"],
                relationship=self.neo4j_queries_manager.get_article_publisher_relationship(),
                uuid_label="identifier")

            # 5. Text Rank
            gv.logger.info("Computing Text Rank!")
            text_score = compute_text_score(self.es_connector, graph, uuid=data["identifier"],
                                            label_a=self.neo4j_queries_manager.article_node_label,
                                            label_b=self.neo4j_queries_manager.publisher_node_label,
                                            relationship=self.neo4j_queries_manager.article_publisher_relationship,
                                            art_index=self.art_index, relevance=article_rank)
            scores.update({"text_rank": text_score})

            # 6. Media Type Rank
            gv.logger.info("Computing Media Type Rank!")
            media_type_score = compute_media_type_score(data["url"], csv_filepath=self.media_type_csv)
            scores.update({"media_type_rank": media_type_score})

        except Exception as e:
            gv.logger.error(e)
        return scores

    def update_properties_in_graph(self, graph: Graph, entity: str, uuid: str, data: dict):
        try:
            for k, v in data.items():
                self.neo4j_connector.update_neo4j_property(graph, label=entity.title(),
                                                           uuid_label="identifier",
                                                           uuid=uuid, property=k,
                                                           value=v)
        except Exception as e:
            gv.logger.error(e)

    @staticmethod
    def get_publisher_scores_importances():
        non_importances = np.array([])
        try:
            # Page rank || Twitter || Suffix || Text || Media Type
            non_importances = np.array([stats.norm.pdf(0.5), stats.norm.pdf(0),
                                        stats.norm.pdf(2), stats.norm.pdf(1),
                                        stats.norm.pdf(0.5)
                                    ])
        except Exception as e:
            gv.logger.error(e)
        return non_importances

    @staticmethod
    def normalize_importances(non_importances):
        return non_importances / np.sum(non_importances)

    @staticmethod
    def get_author_scores_importances():
        non_importances = np.array([])
        try:
            # Text Features || Publisher score
            non_importances = np.array([stats.norm.pdf(2), stats.norm.pdf(0)])
        except Exception as e:
            gv.logger.error(e)
        return non_importances

    @staticmethod
    def get_scores_values(scores):
        scores_values = np.array([])
        try:
            scores_norm = [round(i, 2) for i in list(scores.values())]
            scores_values = np.array(scores_norm)
        except Exception as e:
            gv.logger.error(e)
        return scores_values

    @staticmethod
    def calculate_multimodal_score(scores, importances):
        multimodal_score: float = -1
        try:
            if (scores.shape[0] > 0) and (importances.shape[0] > 0):
                multimodal_score: float = float(np.dot(scores, importances))

        except Exception as e:
            gv.logger.error(e)
        return multimodal_score

    @staticmethod
    def get_basic_information_from_publisher(full_domain: str, csv_filepath: str):
        domain, df_websites, domain_data = None, None, None
        try:
            domain, df_websites, domain_data = collect_domain_info_from_db(
                full_domain, csv_filepath)
        except Exception as e:
            gv.logger.error(e)
        return domain, df_websites, domain_data

    @staticmethod
    def get_feature_scores_from_publisher(graph, label, uuid):
        feature_scores = None
        try:
            feature_scores = get_data_from_neo4j(graph, label, uuid)
        except Exception as e:
            gv.logger.error(e)
        return feature_scores

    def retrieve_source_information(self, graph, full_domain, es_connector, es_index):
        output_response = {}
        try:
            gv.logger.info("Retrieving basic information for URL: %s", full_domain)
            # 1) Retrieve Basic information
            domain, df_websites, domain_data = self.get_basic_information_from_publisher(
                full_domain=full_domain,
                csv_filepath=self.media_type_csv)
            output_response.update({"source_information": domain_data})
            data_uuid = [domain]

            # 2) Retrieve Twitter information
            if self.twitter_api is None:
                self.set_up_twitter_connection()
            if self.twitter_score_func is None:
                self.set_up_twitter_score_function()

            gv.logger.info("Retrieving information from Twitter ...")
            user_item = get_user_by_username(api=self.twitter_api, username=domain)
            user_data = get_user_data(user_item)

            output_response.update({"twitter_information": user_data})

            # Generate UUID for publisher and retrieve its value from Elasticsearch
            uuid_pub = ElasticsearchManager.generate_uuid_from_string(data_uuid=data_uuid)
            if es_connector is not None:
                response = es_connector.retrieve_data_from_index_by_id(index=es_index,
                                                                       uuid=uuid_pub)
            else:
                response = {}
            #  3) Retrieve Neo4j features
            if response:
                gv.logger.info("Retrieving information from NEO4J...")
                available_fandango = True
                features_neo4j = self.get_feature_scores_from_publisher(
                    graph=graph,
                    label=self.neo4j_queries_manager.get_publisher_node_label(),
                    uuid=uuid_pub)
            else:
                gv.logger.info("Domain %s not available yet in FANDANGO ...", domain)
                available_fandango = False
                pub_data = {"name": domain, "url": domain, "identifier": uuid_pub}

                # Get scores and importances
                response_twitter = {"analyse": True, "score": -1}
                scores_data, non_importances = self.get_scores_importances_from_publisher(
                    graph, pub_data,
                    response_twitter=response_twitter)
                non_importances_ls = change_importance(data=scores_data, key="text_rank",
                                                       importance_data=non_importances, new_importance=0)
                scores = self.get_scores_values(scores_data)
                importances = self.normalize_importances(np.array(non_importances_ls))
                features_neo4j = dict(zip(list(scores_data.keys()), scores))
                non_trustworthiness = self.calculate_multimodal_score(scores, importances)

                # Normalize trustworthiness
                trustworthiness = normalize_trustworthiness(non_trustworthiness)
                features_neo4j.update({"trustworthiness": trustworthiness})

            features_neo4j["available_fandango"] = available_fandango
            output_response.update({"neo4j_information": features_neo4j})
            gv.logger.info("Done!")
        except Exception as e:
            gv.logger.info(e)
        return output_response

    def get_scores_importances_from_publisher(self, graph, data, response_twitter:{dict}):
        scores_data, non_importances = {}, np.array([])
        try:
            scores_data: dict = self.compute_publisher_scores(graph, data, response_twitter)
            non_importances: np.array = self.get_publisher_scores_importances()
        except Exception as e:
            gv.logger.error(e)
        return scores_data, non_importances

    def get_scores_importances_from_author(self, graph, data):
        scores_data, importances = {}, np.array([])
        try:
            scores_data: dict = self.compute_author_scores(graph, data)
            importances: np.array = self.get_author_scores_importances()
        except Exception as e:
            gv.logger.error(e)
        return scores_data, importances
