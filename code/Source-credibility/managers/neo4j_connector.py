import pandas as pd
import os
from py2neo import Graph
from helper import global_variables as gv
from managers.neo4j_queries import Neo4jQueries
from models.graph_models import Neo4jInputDoc, Neo4jOutputDoc
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
        self.default_field = gv.org_default_field
        self.sheet_names_tld = gv.sheet_names_tld
        self.score_name = gv.score_name
        self.filepath_tld = os.path.join(gv.resources_dir, gv.filepath_tld)
        self.connection = False
        self.person_index = gv.person_es_index
        self.publisher_index = gv.org_es_index
        self.centrality_rank_name = gv.centrality_rank_name
        self.anonymous_rank_name = gv.anonymous_rank_name
        self.csv_filepath = os.path.join(gv.resources_dir, gv.csv_filepath)
        self.source_credibility_analyzer = None

    def connect_to_neo4j_graph(self):
        try:
            uri = self.protocol + "://" + self.host + ':' + self.port + "/db/data/"
            self.graph = Graph(uri=uri, auth=(self.username, self.password))
            # Verify connection by running a query
            self.graph.run("Match () Return 1 Limit 1")
            self.connection = True

        except ConnectionError as ce:
            gv.logger.error(ce)
            self.connection = False
            self.graph = None

        except Exception as e:
            gv.logger.error(e)
            self.connection = False
            self.graph = None

    def build_graph(self, data_tables: dict):
        response: Neo4jOutputDoc = Neo4jOutputDoc(message=gv.http_response_500,
                                                  status=500)
        try:
            # 1. Apply constraints
            # If the graph is empty
            if len(self.graph.schema.node_labels) == 0 and len(self.graph.schema.relationship_types) == 0:
                # New Graph
                labels: list = [self.neo4j_queries_manager.article_node_label,
                                self.neo4j_queries_manager.author_node_label,
                                self.neo4j_queries_manager.publisher_node_label]
                for label in labels:
                    query = self.neo4j_queries_manager.constraint_query(
                        label=label)
                    self.run_query(graph=self.graph, query=query)

            # 2. Create nodes
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

            # 3. Add Relationships
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

            # 4. Generate Response
            response.message: str = gv.http_response_200
            response.status: int = 200

        except Exception as e:
            gv.logger.error(e)
        return response

    @staticmethod
    def create_tables_from_dict(data: Neo4jInputDoc):
        response_data: dict = {"article_table": pd.DataFrame([]),
                               "authors_table": pd.DataFrame([]),
                               "publisher_table": pd.DataFrame([])}
        response: Neo4jOutputDoc = Neo4jOutputDoc(message=gv.http_response_500,
                                                  status=500,
                                                  data=response_data)
        try:
            # 1. Retrieve Data
            dict_aut: dict = data.authors
            dict_pub: dict = data.publisher
            dict_art: dict = data.article

            # 2. Add identifiers
            dict_art["author"] = data.authors["identifier"]
            dict_art["publisher"] = data.publisher["identifier"]

            transformed_dict_aut = join_dict_from_nested_list(nested_dict=dict_aut,
                                                              ls1_id=list(dict_aut.keys())[0],
                                                              ls2_id=list(dict_aut.keys())[1])
            transformed_dict_pub = join_dict_from_nested_list(nested_dict=dict_pub,
                                                              ls1_id=list(dict_pub.keys())[0],
                                                              ls2_id=list(dict_pub.keys())[1])

            # 3. Create DataFrames
            df_person: pd.DataFrame = pd.DataFrame(transformed_dict_aut)
            df_pub: pd.DataFrame = pd.DataFrame(transformed_dict_pub)
            df_article: pd.DataFrame = pd.DataFrame.from_dict(
                dict_art, orient='index').transpose()

            # 4. Add to response data
            response_data["article_table"]: pd.DataFrame = df_article
            response_data["authors_table"]: pd.DataFrame = df_person
            response_data["publisher_table"]: pd.DataFrame = df_pub

            # 5. Update final response
            response.message: str = gv.http_response_200
            response.status: int = 200
            response.data: dict = response_data

        except Exception as e:
            gv.logger.error(e)
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
                    gv.logger.warning(e)
                    continue
            # Commit the process
            tx.commit()
        except Exception as e:
            gv.logger.warning(e)
            response = {"status": 400, "error": str(e)}
        return response

    @staticmethod
    def run_query(graph, query):
        response = {"status": 200, "error": ""}
        try:
            response["data"] = graph.run(query)
        except Exception as e:
            gv.logger.error(e)
            response = {"status": 400, "error": str(e), "data": []}
        return response

    @staticmethod
    def get_data_from_query(graph, query):
        response = None
        try:
            response = graph.run(query).data()
        except Exception as e:
            gv.logger.error(e)
        return response

    @staticmethod
    def remove_database(graph):
        response = {"status": 200, "error": ""}
        try:
            query = """MATCH (n) DETACH DELETE n"""
            graph.run(query)
        except Exception as e:
            gv.logger.error(e)
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
            gv.logger.error(e)
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
            gv.logger.error(e)
        return response