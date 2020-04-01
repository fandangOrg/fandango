import datetime
import os
from helper import config as cfg
from models.author import Author
from models.publisher import Publisher
from helper.helper import extract_domain_from_url
from helper import global_variables as gv
from threading import Thread
from graph_analysis.source_credibility_analysis import SourceCredibility


class GraphAnalysis:
    def __init__(self, neo4j_connector, elasticsearch_connector):
        self.neo4j_connector = neo4j_connector
        self.elasticsearch_connector = elasticsearch_connector
        self.source_credibility_analyzer = SourceCredibility(es_connector=elasticsearch_connector,
                                                             neo4j_connector=neo4j_connector)
        self.person_index = cfg.person_es_index
        self.publisher_index = cfg.org_es_index
        self.csv_filepath = os.path.join(cfg.resources_dir, cfg.csv_filepath)
        self.countries_website = cfg.countries_websites

    def extract_authors_from_document(self, document):
        author_data = {"identifier": [], "source_data": []}
        try:
            domain_info = extract_domain_from_url(document.url)
            source_domain = domain_info.domain
            for aut_name in document.authors:
                # Considering Name + source_domain
                uuid_aut = self.elasticsearch_connector.generate_uuid_from_string(data_uuid=[aut_name,
                                                                                             source_domain])

                # Check if the author is already in Elasticsearch by uuid
                response = self.elasticsearch_connector.retrieve_data_from_index_by_id(index=self.person_index,
                                                                                       uuid=uuid_aut)
                source_data = response
                # If it does not exist yet
                if not response:
                    author_obj = Author(identifier=uuid_aut, name=aut_name, affiliation=document.publisher,
                                        url=document.url)
                    source_data = author_obj.to_source_data_dict()
                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(index=self.person_index,
                                                                                 uuid=uuid_aut,
                                                                                 source_data=source_data)
                # Append data to response
                author_data["identifier"].append(uuid_aut)
                author_data["source_data"].append(source_data)
        except Exception as e:
            cfg.logger.error(e)
        return author_data

    def extract_publisher_from_document(self, document):
        publisher_data = {"identifier": [], "source_data": []}
        try:
            if not isinstance(document.publisher, list):
                document.publisher = [document.publisher]

            for pub_name in document.publisher:
                domain_info = extract_domain_from_url(document.url)
                url = domain_info.domain
                data_uuid = [url]

                # Check if the publisher is already in Elasticsearch by uuid
                uuid_pub = self.elasticsearch_connector.generate_uuid_from_string(data_uuid=data_uuid)
                response = self.elasticsearch_connector.retrieve_data_from_index_by_id(index=self.publisher_index,
                                                                                       uuid=uuid_pub)
                source_data = response
                # If it does not exist yet
                if not response:
                    pub_obj = Publisher(identifier=uuid_pub, name=pub_name, url=document.sourceDomain,
                                        country=document.country, nationality=document.nationality)

                    source_data = pub_obj.to_source_data_dict()

                    # Bulk data into
                    res_bulk = self.elasticsearch_connector.bulk_data_into_index(index=self.publisher_index,
                                                                                 uuid=uuid_pub,
                                                                                 source_data=source_data)
                # Append data to response
                publisher_data["identifier"].append(uuid_pub)
                publisher_data["source_data"].append(source_data)
        except Exception as e:
            cfg.logger.error(e)
        return publisher_data

    def apply_graph_analysis(self, document):
        response = {}
        try:
            # 1) Extract Authors from document
            authors_data = self.extract_authors_from_document(document=document)

            # 2) Extract Publisher
            publisher_data = self.extract_publisher_from_document(document=document)

            # 3) Merge data
            document_neo4j = {'Article': document.article_to_dict(),
                              'Authors': authors_data, 'Publisher': publisher_data}

            # 4) Add to queue
            self.add_document_to_queue(document=document_neo4j)

            # 5) Generate response
            response = self.build_graph_response(id=document.identifier, authors_data=authors_data,
                                                 publisher_data=publisher_data)

            # 5) check queue status process
            self.start_neo4j_thread_process()
        except Exception as e:
            cfg.logger.error(e)
        return response

    def add_document_to_queue(self, document):
        try:
            gv.queue_neo4j.put(document)
            gv.event.set()
        except Exception as e:
            cfg.logger.error(e)
        return self

    def start_neo4j_thread_process(self):
        try:
            if gv.thread_neo4j is None:
                gv.thread_neo4j = Thread(target=self.analyse_data_from_neo4j_queue)
                gv.thread_neo4j.start()
        except Exception as e:
            cfg.logger.error(e)
        return self

    def analyse_data_from_neo4j_queue(self):
        try:
            while not gv.queue_neo4j.empty():
                cfg.logger.warning('Neo4j Thread Process')
                neo4j_data = gv.queue_neo4j.get()

                # Start graph process
                response = self.source_credibility_analyzer.start_source_credibility_analysis(
                    document=neo4j_data)
                # Update ES scores
                self.update_trustworthiness_analysis(data_to_update=response,
                                                     keys=list(response.keys()))
                cfg.logger.info("Document " + neo4j_data['Article']["identifier"] +
                                " was added and analyzed correctly in NEO4J Graph" +
                                " at " + (datetime.datetime.now().strftime("%c")) + "\n")
                # -------------------------------------------------------
                gv.event.clear()
                # End process
                if gv.queue_neo4j.empty():
                    gv.event.wait()
                    gv.event.clear()
                # -------------------------------------------------------
            cfg.logger.warning('No more data to be analysed!')
        except Exception as e:
            cfg.logger.error(e)
        return self

    @staticmethod
    def build_graph_response(id, authors_data, publisher_data):
        response = {"identifier": "", "authors": [], "publisher": []}
        try:
            authors_uuids = authors_data["identifier"]
            publisher_uuid = publisher_data["identifier"]
            response = {"identifier": id, "authors": authors_uuids, "publisher": publisher_uuid}
        except Exception as e:
            cfg.logger.error(e)
        return response

    def update_trustworthiness_analysis(self, data_to_update, keys):
        try:
            for k in keys:
                n_elements = len(data_to_update[k]["uuids"])
                for i in range(n_elements):
                    uuid = data_to_update[k]["uuids"][i]
                    trustworthiness = data_to_update[k]["scores"][i]
                    status = data_to_update[k]["status"][i]
                    index = data_to_update[k]["index"][i]
                    params = {"trustworthiness": trustworthiness, "status": status}
                    body = {"doc": params}
                    self.elasticsearch_connector.update_fields_to_index(index=index, uuid=uuid,
                                                                        body=body)
        except Exception as e:
            cfg.logger.error(e)
        return self


    def analyse_publisher_ui(self, full_domain):
        response = {}
        try:
            response = self.source_credibility_analyzer.retrieve_source_information(graph=self.neo4j_connector.graph,
                                                                                    full_domain=full_domain,
                                                                                    es_connector=self.elasticsearch_connector,
                                                                                    es_index=self.publisher_index)
        except Exception as e:
            cfg.logger.error(e)
        return response