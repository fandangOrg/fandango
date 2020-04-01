import pandas as pd
import os
from py2neo import Graph
from helper import config as cfg
from managers.neo4j_queries import Neo4jQueries
from helper.helper import join_dict_from_nested_list


class NEO4JConnector:
    def __init__(self, host, port, username, password, protocol):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.protocol = protocol
        self.graph = None
        self.neo4j_queries_manager = Neo4jQueries()
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
        self.source_credibility_analyzer = None

    def connect_to_neo4j_graph(self):
        try:
            uri = self.protocol + "://" + self.host + ':' + self.port + "/db/data/"
            self.graph = Graph(uri=uri, auth=(self.username, self.password))
            self.connection = True
        except Exception as e:
            cfg.logger.error(e)
            self.connection = False
            self.graph = None
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