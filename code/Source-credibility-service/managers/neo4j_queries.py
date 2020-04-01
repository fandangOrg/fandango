from models.author import Author
from models.publisher import Publisher
from models.article import Article
import json
from helper import config as cfg


class Neo4jQueries:
    def __init__(self):
        self.author_node_label = "Author"
        self.publisher_node_label = "Publisher"
        self.article_node_label = "Article"
        self.article_author_relationship = "WAS_WRITTEN_BY"
        self.article_publisher_relationship = "WAS_PUBLISHED_BY"
        self.author_publisher_relationship = "IS_AFFILIATED_TO"

    def get_publisher_node_label(self):
        return self.publisher_node_label
    def get_article_node_label(self):
        return self.article_node_label
    def get_author_node_label(self):
        return self.author_node_label
    def get_article_author_relationship(self):
        return self.article_author_relationship
    def get_article_publisher_relationship(self):
        return self.article_publisher_relationship
    def get_author_publisher_relationship(self):
        return self.author_publisher_relationship

    @staticmethod
    def create_author_node(label):
        query = None
        try:
            author_keys = list(Author().author_to_dict().keys())
            author_values = ["$" + k for k in author_keys]
            params = json.dumps(dict(zip(author_keys, author_values))).replace(": ", ":"). replace('\"', "")
            query = """MERGE (a:LABEL PARAMS)""".replace("PARAMS", params).replace("LABEL", label)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def create_publisher_node(label):
        query = None
        try:
            pub_keys = list(Publisher().publisher_to_dict().keys())
            pub_values = ["$" + k for k in pub_keys]
            params = json.dumps(dict(zip(pub_keys, pub_values))).replace(": ", ":"). replace('\"', "")
            query = """MERGE (a:LABEL PARAMS)""".replace("PARAMS", str(params)).replace("LABEL",label)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def create_article_node(label):
        query = None
        try:
            art_keys = Article().get_required_properties()
            art_values = ["$" + k for k in art_keys]
            params = json.dumps(dict(zip(art_keys, art_values))).replace(": ", ":"). replace('\"', "")
            query = """MERGE (a:LABEL PARAMS)""".replace("PARAMS", params).replace("LABEL",
                                                                                         label)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def constraint_query(label, uuid="identifier"):
        query = None
        try:
            query = """CREATE CONSTRAINT ON (i:LABEL) ASSERT (i.UUID) 
            IS UNIQUE""".replace("LABEL", label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def create_relationship(label_a, label_b, relationship, unwind="author", uuid="identifier"):
        query = None
        try:
            query = """MATCH(i:LABEL_A) UNWIND i.UNWIND_PARAM as param MATCH(a:LABEL_B) WHERE param = a.UUID MERGE (i)-[:RELATIONSHIP]-(a)""".replace(
                "LABEL_A", label_a).replace("LABEL_B", label_b).replace("UNWIND_PARAM", unwind).replace("UUID", uuid).replace("RELATIONSHIP", relationship)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def create_undirect_relationship(label_a, label_b, label_c, relationship, unwind_b="publisher", unwind_c="author", uuid="identifier"):
        query = None
        try:
            query_doc = """MATCH(i:LABEL_A) WITH i UNWIND i.UNWIND_PARAMS_B as param_b UNWIND i.UNWIND_PARAMS_C as param_c MATCH(o:LABEL_B) MATCH(a:LABEL_C) WHERE param_c = a.UUID AND param_b =o.UUID MERGE (a)-[:RELATIONSHIP]-(o)"""
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("LABEL_C", label_c).replace(
                "RELATIONSHIP", relationship).replace(
                "UNWIND_PARAMS_B", unwind_b).replace("UNWIND_PARAMS_C", unwind_c).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def create_rank_query(algorithm, label, relationship, damping_factor=0.75, uuid="identifier"):
        query = None
        try:
            query_doc = """CALL algo.ALGORITHM.stream('LABEL', 'RELATIONSHIP', {iterations:20, dampingFactor:DAMPINGFACTOR})
            YIELD nodeId, score RETURN algo.asNode(nodeId).name AS name,
            algo.asNode(nodeId).IDENTIFIER as IDENTIFIER, score ORDER BY score DESC"""
            query = query_doc.replace(
                "LABEL", label).replace("RELATIONSHIP", relationship).replace(
                "DAMPINGFACTOR", str(damping_factor)).replace("IDENTIFIER", uuid).replace("ALGORITHM", algorithm)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_total_nodes_by_relationship(label_a, label_b, relationship, uuid, uuid_label="identifier"):
        query = None
        try:
            query_doc = """MATCH (a:LABEL_A)-[r:RELATIONSHIP]-(n:LABEL_B) WHERE n.UUID_LABEL="UUID" RETURN COUNT(a) as Total"""
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("RELATIONSHIP", relationship).replace(
                "UUID_LABEL", uuid_label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_nodes_ids_by_relationship(label_a, label_b, relationship, uuid, uuid_label="identifier"):
        query = None
        try:
            query_doc = """MATCH (a:LABEL_A)-[r:RELATIONSHIP]-(n:LABEL_B) WHERE n.UUID_LABEL="UUID" RETURN (a.UUID_LABEL) as Identifiers"""
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("RELATIONSHIP", relationship).replace(
                "UUID_LABEL", uuid_label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_nodes_by_relationship(label_a, label_b, relationship, uuid, uuid_label="identifier"):
        query = None
        try:
            query_doc = """MATCH (a:LABEL_A)-[r:RELATIONSHIP]-(n:LABEL_B) WHERE a.UUID_LABEL="UUID" RETURN n as publisher
                        """
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("RELATIONSHIP", relationship).replace(
                "UUID_LABEL", uuid_label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_nodes_by_relationship_opposite(label_a, label_b, relationship, uuid, uuid_label="identifier"):
        query = None
        try:
            query_doc = """MATCH (a:LABEL_A)-[r:RELATIONSHIP]-(n:LABEL_B) WHERE n.UUID_LABEL="UUID" RETURN a as 
            data"""
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("RELATIONSHIP", relationship).replace(
                "UUID_LABEL", uuid_label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_total_nodes_by_property(label_a, label_b, relationship, uuid, uuid_label="identifier"):
        query = None
        try:
            query_doc = """MATCH (a:LABEL_A)-[r:RELATIONSHIP]-(n:LABEL_B) WHERE n.IDENTIFIER_LABEL=~'.*UUID.*' RETURN COUNT(a) as Total"""
            query = query_doc.replace("LABEL_A", label_a).replace(
                "LABEL_B", label_b).replace("RELATIONSHIP", relationship).replace(
                "IDENTIFIER_LABEL", uuid_label).replace("UUID", uuid)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def set_property_to_node(label, uuid_label, uuid, property, value):
        query = None
        try:
            query_doc = """MATCH (n:LABEL { IDENTIFIER: "UUID_VAL" }) SET n.PROPERTY = toString('VALUE')"""
            query = query_doc.replace("LABEL", label).replace(
                "IDENTIFIER", uuid_label).replace("UUID_VAL", uuid).replace(
                "PROPERTY", property).replace("VALUE", str(value))
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def count_nodes_same_label(label):
        query = None
        try:
            query_doc = """MATCH (n:LABEL) RETURN count(n) as total"""
            query = query_doc.replace("LABEL", label)
        except Exception as e:
            cfg.logger.error(e)
        return query

    @staticmethod
    def get_node_by_property(label, property_label, property):
        query = None
        try:
            query_doc = """MATCH (n:LABEL {PROPERTY_KEY : "VALUE"}) RETURN n as data"""
            query = query_doc.replace("LABEL", label).replace(
                "PROPERTY_KEY", property_label).replace("VALUE", property)
        except Exception as e:
            cfg.logger.error(e)
        return query
