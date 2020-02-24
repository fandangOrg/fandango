import datetime
import pandas as pd
import os
import numpy as np
import tldextract
from py2neo import Graph
from helper import config as cfg
from helper.neo4j_queries import Neo4jQueries
from helper.helper import (read_tld_data, extract_country_tld_weight, get_distance_between_dates,
                           extract_publisher_info, get_datetime_from_str, normalize_value,
                           normalize_trustworthiness, join_dict_from_nested_list,
                           fuzzy_distance, sigmoid, analyze_url, get_weighted_average,
                           retrieve_neo4j_features_from_db,read_csv_file, extract_domain_info_from_df,
                           extract_domain_from_url)


class NEO4JConnector:
    def __init__(self, host, port, username, password, protocol):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.protocol = protocol
        self.graph = None
        self.neo4j_queries_manager = Neo4jQueries()
        self.initial_rank = cfg.initial_rank
        self.default_field = cfg.org_default_field
        self.sheet_names_tld = cfg.sheet_names_tld
        self.score_name = cfg.score_name
        self.filepath_tld = os.path.join(cfg.resources_dir, cfg.filepath_tld)
        self.connection = False
        self.person_index = cfg.person_es_index
        self.publisher_index = cfg.org_es_index
        self.centrality_rank_name = cfg.centrality_rank_name
        self.anonymous_rank_name = cfg.anonymous_rank_name
        self.csv_filepath = os.path.join(cfg.resources_dir, cfg.csv_filepath)

    def connect_to_neo4j_graph(self):
        try:
            uri = self.protocol + "://" + self.host + ':' + self.port + "/db/data/"
            self.graph = Graph(uri=uri, auth=(self.username, self.password))
            self.connection = True
        except Exception as e:
            cfg.logger.error(e)
            self.connection = True
        return self

    def build_graph(self, data_tables):
        try:
            # 2) Apply constraints
            # If the graph is empty
            if len(self.graph.schema.node_labels) == 0 and len(self.graph.schema.relationship_types) == 0:
                # New Graph
                labels = [self.neo4j_queries_manager.article_node_label,
                          self.neo4j_queries_manager.author_node_label,
                          self.neo4j_queries_manager.publisher_node_label]
                for label in labels:
                    query = self.neo4j_queries_manager.constraint_query(
                        label=label)
                    self.run_query(graph=self.graph, query=query)

            # 3) Create nodes
            # a) Article
            query = self.neo4j_queries_manager.create_article_node(label=self.neo4j_queries_manager.article_node_label)
            self.create_node_from_df(graph=self.graph, query=query, df=data_tables["article_table"])

            # b) Author
            query = self.neo4j_queries_manager.create_author_node(label=self.neo4j_queries_manager.author_node_label)
            self.create_node_from_df(graph=self.graph, query=query, df=data_tables["authors_table"])

            # c) Publisher
            query = self.neo4j_queries_manager.create_publisher_node(
                label=self.neo4j_queries_manager.publisher_node_label)
            self.create_node_from_df(graph=self.graph, query=query, df=data_tables["publisher_table"])

            # 4) Add Relationships
            query = self.neo4j_queries_manager.create_relationship(
                label_a=self.neo4j_queries_manager.article_node_label,
                label_b=self.neo4j_queries_manager.author_node_label,
                relationship=self.neo4j_queries_manager.article_author_relationship)
            self.run_query(graph=self.graph, query=query)

            query = self.neo4j_queries_manager.create_relationship(
                label_a=self.neo4j_queries_manager.article_node_label,
                label_b=self.neo4j_queries_manager.publisher_node_label,
                unwind="publisher",
                relationship=self.neo4j_queries_manager.article_publisher_relationship)
            self.run_query(graph=self.graph, query=query)

            query = self.neo4j_queries_manager.create_undirect_relationship(
                label_a=self.neo4j_queries_manager.article_node_label,
                label_b=self.neo4j_queries_manager.publisher_node_label,
                label_c=self.neo4j_queries_manager.author_node_label,
                relationship=self.neo4j_queries_manager.author_publisher_relationship)
            self.run_query(graph=self.graph, query=query)
        except Exception as e:
            cfg.logger.error(e)
        return self

    def start_graph_analysis(self, document):
        response = {}
        try:
            # 1) Generate DataFrames
            data_tables = self.create_tables_from_dict(data=document)

            # 2) build graph
            self.build_graph(data_tables=data_tables)

            # 3) Apply analysis and generate output
            response = self.analyse_trustworthiness(data_tables=data_tables)
        except Exception as e:
            cfg.logger.error(e)
        return response

    @staticmethod
    def create_tables_from_dict(data):
        response = {}
        try:
            dict_aut = data['Authors']
            dict_pub = data['Publisher']
            dict_art = data['Article']

            # Add identifiers
            dict_art["author"] = data["Authors"]["identifier"]
            dict_art["publisher"] = data["Publisher"]["identifier"]

            transformed_dict_aut = join_dict_from_nested_list(nested_dict=dict_aut,
                                                              ls1_id=list(dict_aut.keys())[0],
                                                              ls2_id=list(dict_aut.keys())[1])
            transformed_dict_pub = join_dict_from_nested_list(nested_dict=dict_pub,
                                                              ls1_id=list(dict_pub.keys())[0],
                                                              ls2_id=list(dict_pub.keys())[1])

            # Create DataFrames
            df_person = pd.DataFrame(transformed_dict_aut)
            df_pub = pd.DataFrame(transformed_dict_pub)
            df_article = pd.DataFrame.from_dict(dict_art, orient='index').transpose()

            response = {"article_table": df_article, "authors_table": df_person,
                        "publisher_table": df_pub}
        except Exception as e:
            cfg.logger.error(e)
        return response

    @staticmethod
    def create_node_from_df(graph, query, df):
        response = {"status": 200, "error": ""}
        try:
            # Start graph
            tx = graph.begin()
            for index, row in df.iterrows():
                try:
                    parameters = dict(row)
                    tx.evaluate(query, parameters=parameters)
                except Exception as e:
                    cfg.logger.warning(e)
                    continue
            # Commit the process
            tx.commit()
        except Exception as e:
            cfg.logger.warning(e)
            response = {"status": 400, "error": str(e)}
        return response

    @staticmethod
    def run_query(graph, query):
        response = {"status": 200, "error": ""}
        try:
            response["data"] = graph.run(query)
        except Exception as e:
            cfg.logger.error(e)
            response = {"status": 400, "error": str(e), "data": []}
        return response

    @staticmethod
    def get_data_from_query(graph, query):
        response = None
        try:
            response = graph.run(query).data()
        except Exception as e:
            cfg.logger.error(e)
        return response

    @staticmethod
    def remove_database(graph):
        response = {"status": 200, "error": ""}
        try:
            query = """MATCH (n) DETACH DELETE n"""
            graph.run(query)
        except Exception as e:
            cfg.logger.error(e)
            response = {"status": 400, "error": str(e)}
        return response

    def compute_rank_algorithm(self, uuid, graph, query, default_controller=0.15, label="publisher"):
        rank_score = default_controller
        try:
            query_el = self.neo4j_queries_manager.count_nodes_same_label(label=label.title())
            n_elements = self.get_data_from_query(graph=graph, query=query_el)
            if n_elements[0]["total"] >=2:
                try:
                    rank = self.get_data_from_query(graph=graph, query=query)
                except Exception as e:
                    cfg.logger.warning(e)
                    rank = None
                # Get maximum and minimum
                if rank is not None:
                    max_pr = rank[0]['score']
                    min_pr = rank[-1]['score']
                    # Generate a dictionary with uuid as keys and scores as values
                    new_dict_pr = {item['identifier']: item['score'] for item in rank}
                    # Rank
                    try:
                        rank_score = new_dict_pr[uuid]
                        if max_pr != min_pr:
                            rank_score = (rank_score - min_pr) / (max_pr - min_pr)
                    except Exception as e:
                        rank_score = default_controller
                else:
                    # Default value
                    rank_score = default_controller
        except Exception as e:
            cfg.logger.error(e)
        return rank_score

    # 2) whois Features
    @staticmethod
    def extract_information_from_domain(domain, default_field="N/A",  list_of_websites=None):
        whois_features = {}
        try:
            whois_features = extract_publisher_info(source_domain=domain, list_of_websites=list_of_websites,
                                                    threshold=95, default_str=default_field)
        except Exception as e:
            cfg.logger.error(e)
        return whois_features

    @staticmethod
    def compute_whois_importance(whois_features, threshold=95, default_field="N/A"):
        whois_importance = {"date": cfg.rho_date, "exp_date": cfg.rho_exp_date,
                            "country": cfg.rho_country_whois,
                            "name": cfg.rho_name_whois}
        try:
            if whois_features:
                # Creation Date
                if len(whois_features["creation_date"]) >0:
                    if (isinstance(whois_features["creation_date"], str) and whois_features["creation_date"] != default_field):
                        created_date = get_datetime_from_str(whois_features["creation_date"])
                    elif (not isinstance(whois_features["creation_date"], str) and whois_features["creation_date"] != default_field):
                        created_date = whois_features["creation_date"]
                    else:
                        created_date = None

                    if created_date is not None:
                        difference = get_distance_between_dates(start_date=datetime.datetime.now(),
                                                                end_date=created_date, time="months")
                    else:
                        difference = -cfg.rho_date
                    # ===========================================
                    whois_importance["date"] = difference
                    # ===========================================

                # Expiration Date
                if len(whois_features["expiration_date"]) > 0:
                    if (isinstance(whois_features["expiration_date"], str) and whois_features["expiration_date"] != default_field):
                        exp_date = get_datetime_from_str(whois_features["expiration_date"])
                    elif (not isinstance(whois_features["expiration_date"], str) and whois_features["expiration_date"] != default_field):
                        exp_date = whois_features["expiration_date"]
                    else:
                        exp_date = None

                    if exp_date is not None:
                        difference_exp = get_distance_between_dates(start_date=exp_date,
                                                                    end_date=datetime.datetime.now(), time="months")
                    else:
                        difference_exp = -cfg.rho_exp_date
                    # ===========================================
                    whois_importance["exp_date"] = difference_exp
                    # ===========================================
                # Country
                if (whois_features["country"] != cfg.org_default_field or
                        whois_features["whois_country"] != cfg.org_default_field):
                    # ===========================================
                    whois_importance["country"] = cfg.rho_country_whois
                    # ===========================================
                else:
                    # ===========================================
                    whois_importance["country"] = -cfg.rho_country_whois
                    # ===========================================
                # Name
                if whois_features["whois_name"] != default_field:
                    similarity = fuzzy_distance(str_1=whois_features["name"], str_2=whois_features["whois_name"])
                    if similarity >= threshold:
                        # ===========================================
                        whois_importance["name"] = cfg.rho_name_whois
                        # ===========================================
                    else:
                        # ===========================================
                        whois_importance["name"] = -cfg.rho_name_whois
                        # ===========================================
                else:
                    whois_importance["name"] = -cfg.rho_name_whois/2

        except Exception as e:
            cfg.logger.error(e)
        return whois_importance

    @staticmethod
    def compute_domain_importance(domain_data):
        domain_importance = {"media_type_importance": -cfg.rho_media_type,
                             "malicious_importance": cfg.rho_malicious}
        try:
            # Malicious
            if domain_data["malicious"]:
                domain_importance["media_type_importance"] = - cfg.rho_malicious
            else:
                domain_importance["media_type_importance"] = cfg.rho_malicious

            if domain_data["media_type"] == "Broadcast" or domain_data["media_type"] == "Press Agency":
                domain_importance["media_type_importance"] = cfg.rho_media_type
            elif domain_data["media_type"] == "Newspaper":
                domain_importance["media_type_importance"] = cfg.rho_media_type
            elif domain_data["media_type"] == "Magazine":
                domain_importance["media_type_importance"] = cfg.rho_media_type/2
            else:
                domain_importance["media_type_importance"] = -cfg.rho_media_type
        except Exception as e:
            cfg.logger.error(e)
        return domain_importance

    # 3) TLD Features
    @staticmethod
    def compute_suffix_importance(domain, sheet_names, filepath, key="importance_weight"):
        suffix_vector = {"suffix": "", key: cfg.rho_suffix, "additional_data": {}}
        try:
            ext = tldextract.extract(domain)
            suffix = ""
            if "suffix" in ext._fields:
                suffix = '.' + ext.suffix
            suffix_vector["suffix"] = suffix

            # extract tld data
            tld_data = read_tld_data(filepath=filepath, sheet_names=sheet_names)
            # Add importance weight column
            tld_data[sheet_names[0]][key] = tld_data[sheet_names[0]].apply(extract_country_tld_weight, axis=1)
            tld_data[sheet_names[1]][key] = [cfg.rho_com_suffix, cfg.rho_org_suffix, cfg.rho_net_suffix,
                                             cfg.rho_int_suffix, cfg.rho_edu_suffix, cfg.rho_gov_suffix,
                                             cfg.rho_mil_suffix]

            # Get the suffix importance
            country_res = tld_data[sheet_names[0]].loc[tld_data[sheet_names[0]]['Name'] == suffix].to_dict()
            if country_res[key]:
                suffix_vector[key] = list(country_res[key].values())[0]
                values = [list(country_res[kk].values())[0] for kk in country_res]
                keys = list(country_res.keys())
                suffix_vector["additional_data"] = dict(zip(keys, values))
                suffix_vector["additional_data"]["Administrator"] = cfg.org_default_field
            else:
                orig_res = tld_data[sheet_names[1]].loc[tld_data[sheet_names[1]]['Name'] == suffix].to_dict()
                if orig_res[key]:
                    suffix_vector[key] = list(orig_res[key].values())[0]
                    values = [list(orig_res[kk].values())[0]for kk in orig_res]
                    keys = list(orig_res.keys())
                    suffix_vector["additional_data"] = dict(zip(keys, values))
                else:
                    suffix_vector[key] = -cfg.rho_suffix
                    suffix_vector["additional_data"] = {}

            # Update keys
            keys = list(suffix_vector["additional_data"].keys())
            keys = [kk.lower() for kk in keys]
            values = list(suffix_vector["additional_data"].values())
            suffix_vector["additional_data"] = dict(zip(keys, values))

        except Exception as e:
            cfg.logger.error(e)
        return suffix_vector

    def compute_anonymous_percentage(self, graph, label_a, label_b, relationship, uuid, neo4j_query=True):
        anonymous_importance = -3
        try:
            if neo4j_query:
                # 2) Anonymous
                query_total = self.neo4j_queries_manager.get_total_nodes_by_relationship(label_a=label_a,
                                                                                         label_b=label_b,
                                                                                         relationship=relationship,
                                                                                         uuid=uuid,
                                                                                         uuid_label="identifier")
                anonymoys_name = self.default_field
                query_anonymous = self.neo4j_queries_manager.get_total_nodes_by_property(label_a=label_a,
                                                                                             label_b=label_b,
                                                                                             relationship=relationship,
                                                                                             uuid=anonymoys_name,
                                                                                             uuid_label="name")
                response = self.get_data_from_query(graph=graph, query=query_total)
                total = response[0]['Total']
                response_anonymous = self.get_data_from_query(graph=graph, query=query_anonymous)
                anonymous = response_anonymous[0]['Total']
                if anonymous == total:
                    anonymous_importance = np.sqrt(total)
                else:
                    anonymous_importance = np.sqrt(total) * (total - anonymous)
            else:
                # Author anonymous
                if self.default_field in uuid:
                    anonymous_importance = -3
                else:
                    anonymous_importance = 3
        except Exception as e:
            cfg.logger.error(e)
        return anonymous_importance

    def compute_centrality_rank(self, graph, label, uuid, uuid_label,relationship, default_controller=0.63):
        centrality_rank = -1
        try:
            query_art_rank = self.neo4j_queries_manager.create_rank_query(algorithm="articleRank",
                                                                          label=label,
                                                                          relationship=relationship,
                                                                          damping_factor=default_controller,
                                                                          uuid=uuid_label)

            query_eigen_rank = self.neo4j_queries_manager.create_rank_query(algorithm="eigenvector",
                                                                            label=label,
                                                                            relationship=relationship,
                                                                            damping_factor=default_controller,
                                                                            uuid=uuid_label)

            art_rank = self.compute_rank_algorithm(uuid=uuid, graph=graph, query=query_art_rank,
                                                       default_controller=default_controller)
            eigen_rank = self.compute_rank_algorithm(uuid=uuid, graph=graph, query=query_eigen_rank,
                                                         default_controller=default_controller)
            centrality_rank = art_rank + eigen_rank
        except Exception as e:
            cfg.logger.error(e)
        return centrality_rank

    @staticmethod
    def get_parameter_controller_matrix(entity="publisher"):
        phi = []
        try:
            if entity == "publisher":
                vector_phi = [cfg.alpha_centrality_rank, cfg.alpha_anonymous,
                              cfg.alpha_date_whois, cfg.alpha_exp_date_whois,
                              cfg.alpha_country_whois, cfg.alpha_name_whois,
                              cfg.alpha_suffix, cfg.alpha_media_type, cfg.alpha_malicious]
            else:
                vector_phi = [0.5, 0.8, 0.2]
            phi = np.diag(vector_phi)
        except Exception as e:
            cfg.logger.error(e)
        return phi

    def analyse_trustworthiness(self, data_tables):
        response = {}
        try:
            # Update Publisher score
            publisher_df = data_tables["publisher_table"]
            authors_df = data_tables["authors_table"]

            publisher_df[self.score_name] = publisher_df.apply(self.compute_trustworthiness_fusion_score,
                                                               args=(self.graph, "publisher"),
                                                               axis=1)
            pub_score = publisher_df[self.score_name].values.tolist()[0]
            authors_df[self.score_name] = authors_df.apply(self.compute_trustworthiness_fusion_score,
                                                           args=(self.graph, "author",pub_score),
                                                           axis=1)
            # Generate output
            # a) Authors
            authors_df_to_dict = authors_df.to_dict()
            authors_uuids = list(authors_df_to_dict["identifier"].values())
            authors_scores = list(authors_df_to_dict[self.score_name].values())
            authors_status = ["done" for i in range(len(authors_uuids))]
            authors_indexes = [self.person_index for i in range(len(authors_uuids))]

            # b) Publisher
            publisher_df_to_dict = publisher_df.to_dict()
            pub_uuids = list(publisher_df_to_dict["identifier"].values())
            pub_scores = list(publisher_df_to_dict[self.score_name].values())
            pub_status = ["done" for i in range(len(pub_uuids))]
            pub_indexes = [self.publisher_index for i in range(len(pub_uuids))]

            # Return output
            response = {"authors": {"uuid": authors_uuids, "scores": authors_scores, "status": authors_status,
                                    "index": authors_indexes},
                        "publisher": {"uuid": pub_uuids, "scores": pub_scores, "status": pub_status,
                                      "index": pub_indexes}}

        except Exception as e:
            cfg.logger.error(e)
        return response

    @staticmethod
    def calculate_domain_features(neo4j_connector, row, graph, entity, relationship):
        total_features = {}
        try:
            centrality_rank = neo4j_connector.compute_centrality_rank(graph=graph, label=entity.title(),
                                                           uuid_label="identifier", relationship=relationship,
                                                           uuid=row["identifier"],
                                                           default_controller=0.63)
            total_features["centrality_rank"] = centrality_rank

            # 2) Anonymous
            label_a = neo4j_connector.neo4j_queries_manager.author_node_label
            relationship = neo4j_connector.neo4j_queries_manager.author_publisher_relationship
            anonymous_importance = neo4j_connector.compute_anonymous_percentage(graph=graph, label_a=label_a,
                                                                     label_b=entity.title(),
                                                                     relationship=relationship,
                                                                     uuid=row["identifier"])
            total_features["anonymous_importance"] = anonymous_importance

            # 3) Whois IP features
            whois_features = neo4j_connector.extract_information_from_domain(domain=row["url"])
            whois_importance = neo4j_connector.compute_whois_importance(whois_features)
            total_features.update(whois_importance)

            # 4) Suffix features
            suffix_features = neo4j_connector.compute_suffix_importance(domain=row["url"],
                                                             sheet_names=neo4j_connector.sheet_names_tld,
                                                             filepath=neo4j_connector.filepath_tld,
                                                             key="importance_weight")
            suffix_importance = {"suffix": suffix_features["importance_weight"]}
            total_features.update(suffix_importance)

        except Exception as e:
            cfg.logger.error(e)
        return total_features

    def collect_domain_info_from_db(self, full_domain):
        domain_data = {"location": cfg.org_default_field,
                       "media_type": cfg.org_default_field,
                       "media_focus": cfg.org_default_field,
                       "language": [],
                       "platform": []}
        domain = None
        df_websites = None
        try:
            # Retrieve domain
            domain = extract_domain_from_url(full_domain)
            df_websites = read_csv_file(self.csv_filepath)
            df_websites = df_websites.fillna("N/A", inplace=False)
            domain_data = extract_domain_info_from_df(df_websites, domain, full_domain)
        except Exception as e:
            cfg.logger.error(e)
        return domain, df_websites, domain_data

    def compute_trustworthiness_fusion_score(self, row, graph, entity, score=None):
        trustworthiness = normalize_value()
        try:
            total_features = {}
            if entity == self.neo4j_queries_manager.publisher_node_label.lower():
                relationship = self.neo4j_queries_manager.article_publisher_relationship
            else:
                relationship = self.neo4j_queries_manager.article_author_relationship
            # ==========================================================================================================
            # 1) Calculate centrality algorithms
            centrality_rank = self.compute_centrality_rank(graph=graph, label=entity.title(),
                                                           uuid_label="identifier", relationship=relationship,
                                                           uuid=row["identifier"],
                                                           default_controller=self.initial_rank)
            # Set Property
            self.update_neo4j_property(graph, label=entity.title(), uuid_label="identifier",
                                       uuid=row["identifier"], property=self.centrality_rank_name,
                                       value=centrality_rank)

            total_features["centrality_rank"] = centrality_rank
            # ==========================================================================================================

            if entity == self.neo4j_queries_manager.publisher_node_label.lower():
                # ======================================================================================================
                # 2) Anonymous
                label_a = self.neo4j_queries_manager.author_node_label
                relationship = self.neo4j_queries_manager.author_publisher_relationship
                anonymous_importance = self.compute_anonymous_percentage(graph=graph, label_a=label_a,
                                                                         label_b=entity.title(),
                                                                         relationship=relationship,
                                                                         uuid=row["identifier"])
                # Set Property
                self.update_neo4j_property(graph, label=entity.title(), uuid_label="identifier",
                                           uuid=row["identifier"], property=self.anonymous_rank_name,
                                           value=anonymous_importance)

                total_features["anonymous_importance"] = anonymous_importance
                # ======================================================================================================
                # 3) Whois IP features
                whois_features = self.extract_information_from_domain(domain=row["url"])
                whois_importance = self.compute_whois_importance(whois_features,
                                                                 default_field=cfg.org_default_field)
                total_features.update(whois_importance)

                # 4) Suffix features
                suffix_features = self.compute_suffix_importance(domain=row["url"],
                                                                 sheet_names=self.sheet_names_tld,
                                                                 filepath=self.filepath_tld,
                                                                 key="importance_weight")
                suffix_importance = {"suffix": suffix_features["importance_weight"]}
                total_features.update(suffix_importance)

                # 5) Domain data
                domain, df_websites, domain_data = self.collect_domain_info_from_db(row["url"])
                domain_data_importance = self.compute_domain_importance(domain_data)
                # malicious_data = analyze_url([row["url"]])
                # malicious_data.update({domain_data[""]})
                total_features.update(domain_data_importance)


                weights = np.array([cfg.w_centrality, cfg.w_anonymous, cfg.w_created_date,
                                    cfg.w_exp_date, cfg.w_country, cfg.w_name, cfg.w_suffix,
                                    cfg.w_media_type, cfg.w_malicious]).reshape((-1, 1))

            elif entity == self.neo4j_queries_manager.author_node_label.lower():
                # 2) Organization score
                pub_score = {"publisher_score": score}
                total_features.update(pub_score)

                # 3) Anonymous author name
                label_a = self.neo4j_queries_manager.author_node_label
                anonymous_importance = self.compute_anonymous_percentage(graph=graph, label_a=label_a,
                                                                         label_b=None,
                                                                         relationship=None,
                                                                         uuid=row["name"],
                                                                         neo4j_query=False)
                total_features["anonymous_importance"] = anonymous_importance
                weights = np.array([cfg.w_centrality, cfg.w_publisher_score, cfg.w_name]).reshape((-1, 1))
            else:
                weights = np.array([])

            # 5) Compute score
            importance_matrix = self.get_parameter_controller_matrix(entity=entity.lower())
            feature_vector = np.array(list(total_features.values()))
            trustworthiness, weighted_importance = self.compute_trustworthiness_score(
                feature_vector=feature_vector,
                importance_matrix=importance_matrix,
                weights=weights)

            # 6) Set property to NEO4J
            self.update_neo4j_property(graph, label=entity.title(), uuid_label="identifier",
                                       uuid=row["identifier"], property=self.score_name, value=trustworthiness)
            self.update_neo4j_property(graph, label=entity.title(), uuid_label="identifier",
                                       uuid=row["identifier"], property="status", value="done")
        except Exception as e:
            cfg.logger.error(e)
        return trustworthiness

    def update_neo4j_property(self, graph, label, uuid_label, uuid, property, value):
        response = {}
        try:
            query = self.neo4j_queries_manager.set_property_to_node(label=label, uuid_label=uuid_label,
                                                                    uuid=uuid, property=property,
                                                                    value=value)
            response = self.run_query(graph, query)
        except Exception as e:
            cfg.logger.error(e)
        return response

    def get_data_from_node(self, graph, label, property_label, domain):
        response = {}
        try:
            query = self.neo4j_queries_manager.get_node_by_property(label, property_label,
                                                                    property=domain)
            data = self.get_data_from_query(graph, query)
            if data:
                response = data[0]["data"]

        except Exception as e:
            cfg.logger.error(e)
        return response

    def get_neo4j_features(self, data):
        response = {self.anonymous_rank_name: cfg.rho_anonymous_rank,
                    self.centrality_rank_name: cfg.rho_centrality_rank,
                    self.anonymous_rank_name + "_importance": cfg.alpha_anonymous,
                    self.centrality_rank_name + "_importance": cfg.alpha_centrality_rank,
                    self.score_name: -1, "available_data": False}
        try:
            if self.anonymous_rank_name in list(data.keys()):
                response[self.anonymous_rank_name] = float(data[self.anonymous_rank_name])
                response["available_data"] = True
            if self.centrality_rank_name in list(data.keys()):
                response[self.centrality_rank_name] = float(data[self.centrality_rank_name])
                response["available_data"] = True
            if self.score_name in list(data.keys()):
                response[self.score_name] = float(data[self.score_name])
                response["available_data"] = True
        except Exception as e:
            cfg.logger.error(e)
        return response

    def extract_neo4j_feature_from_local_db(self, domain, filepath):
        response = {self.anonymous_rank_name: cfg.rho_anonymous_rank,
                    self.centrality_rank_name: cfg.rho_centrality_rank,
                    self.anonymous_rank_name + "_importance": cfg.alpha_anonymous,
                    self.centrality_rank_name + "_importance": cfg.alpha_centrality_rank,
                    self.score_name: -1, "available_data": False}
        try:
            data = retrieve_neo4j_features_from_db(filepath, domain)
            if self.anonymous_rank_name in list(data.keys()):
                response[self.anonymous_rank_name] = float(data[self.anonymous_rank_name])
                response["available_data"] = True
            if self.centrality_rank_name in list(data.keys()):
                response[self.centrality_rank_name] = float(data[self.centrality_rank_name])
                response["available_data"] = True
            if self.score_name in list(data.keys()):
                response[self.score_name] = float(data[self.score_name])
                response["available_data"] = True
        except Exception as e:
            cfg.logger.error(e)
        return response

    @staticmethod
    def compute_trustworthiness_score(feature_vector, importance_matrix, weights):
        trustworthiness = -1
        weighted_importance = np.array([-1 for i in range(weights.shape[0])])
        try:
            score = np.dot(importance_matrix, feature_vector).reshape((-1, 1))
            normalized_score = sigmoid(score).reshape((-1, 1))
            weighted_average, weighted_importance = get_weighted_average(data=normalized_score, weights=weights)
            trustworthiness = 100 * weighted_average
            trustworthiness = normalize_trustworthiness(trustworthiness)
        except Exception as e:
            cfg.logger.error(e)
        return trustworthiness, weighted_importance

    @staticmethod
    def importance_weights_normalized(feature_vector, importance_matrix):
        normalized_importance = importance_matrix
        try:
            importance = np.dot(importance_matrix, feature_vector).reshape((-1, 1))
            normalized_importance = sigmoid(importance).reshape((-1, 1))
        except Exception as e:
            cfg.logger.error(e)
        return normalized_importance