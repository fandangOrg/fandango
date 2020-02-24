import datetime
import os
import numpy as np
from helper import config as cfg
from models.author import Author
from models.publisher import Publisher
from helper import global_variables as gv
from threading import Thread


class GraphAnalysis:
    def __init__(self, neo4j_connector, elasticsearch_connector):
        self.neo4j_connector = neo4j_connector
        self.elasticsearch_connector = elasticsearch_connector
        self.person_index = cfg.person_es_index
        self.publisher_index = cfg.org_es_index
        self.csv_filepath = os.path.join(cfg.resources_dir, cfg.csv_filepath)
        self.countries_website = cfg.countries_websites

    def extract_authors_from_document(self, document):
        author_data = {"identifier": [], "source_data": []}
        try:
            for aut_name in document.authors:
                # Check if the author is already in Elasticsearch by uuid
                uuid_aut = self.elasticsearch_connector.generate_uuid_from_string(data_uuid=[aut_name,
                                                                                             document.identifier])
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
                url = document.sourceDomain
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

            # 6) Generate response
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

                # start graph process
                response = self.neo4j_connector.start_graph_analysis(neo4j_data)
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
                n_elements = len(data_to_update[k]["uuid"])
                for i in range(n_elements):
                    uuid = data_to_update[k]["uuid"][i]
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

    def analyse_source_domain(self, full_domain):
        response = {}
        try:
            # Retrieve domain
            domain, df_websites, domain_data = self.neo4j_connector.collect_domain_info_from_db(full_domain)
            domain_data_importance = self.neo4j_connector.compute_domain_importance(domain_data)


            # 1) Whois Features
            whois_features = self.neo4j_connector.extract_information_from_domain(domain,
                                                                                  default_field=cfg.org_default_field,
                                                                                  list_of_websites=df_websites)
            # 2) Whois importance
            cfg.logger.info("Analysing domain using Whois ... ")
            whois_importance = self.neo4j_connector.compute_whois_importance(whois_features)
            whois_importance_values = [cfg.alpha_date_whois, cfg.alpha_exp_date_whois,
                                       cfg.alpha_country_whois, cfg.alpha_name_whois]
            whois_importance_keys = [str(i) + "_importance" for i in list(whois_importance.keys())]

            whois_importance_data = dict(zip(whois_importance_keys, whois_importance_values))
            whois_importance.update(whois_importance_data)

            # 3) Suffix data
            cfg.logger.info("Analysing domain suffix ... ")
            suffix_features = self.neo4j_connector.compute_suffix_importance(domain=whois_features["domain_name"].lower(),
                                                                             sheet_names=self.neo4j_connector.sheet_names_tld,
                                                                             filepath=self.neo4j_connector.filepath_tld,
                                                                             key="importance_weight")

            # ==========================================================================================================
            # ==========================================================================================================
            response.update(domain_data)
            response.update(domain_data_importance)

            # Whois Features
            response.update({"whois_features": whois_features})
            response.update({"whois_importance": whois_importance})

            # Suffix Features
            response.update({"whois_features": whois_features})
            response.update({"whois_importance": whois_importance})
            response.update({"suffix_information": suffix_features["additional_data"]})

            # Neo4j Features
            cfg.logger.info("Analysing domain in NEO4J ... ")
            label = self.neo4j_connector.neo4j_queries_manager.publisher_node_label
            property_label = "url"
            # TODO: Change Elastic for NEO4J
            # ================================================================================================
            # ================================================================================================
            response_es = self.elasticsearch_connector.retrieve_data_from_index_by_searching(index=self.publisher_index,
                                                                                             search_key="url",
                                                                                             search_value=whois_features["domain_name"].lower(),
                                                                                             fuzzy_threshold=90)
            # ================================================================================================
            # ================================================================================================
            data_node_neo4j = self.neo4j_connector.get_data_from_node(graph=self.neo4j_connector.graph,
                                                                      label=label,
                                                                      property_label=property_label,
                                                                      domain=whois_features["domain_name"])
            neo4j_features = self.neo4j_connector.get_neo4j_features(data_node_neo4j)

            # ==========================================================================================================
            weights = np.array([cfg.w_centrality, cfg.w_anonymous, cfg.w_created_date,
                                cfg.w_exp_date, cfg.w_country, cfg.w_name, cfg.w_suffix,
                                cfg.w_malicious, cfg.w_media_type]).reshape((-1, 1))
            importance_matrix = self.neo4j_connector.get_parameter_controller_matrix(entity=label.lower())
            if neo4j_features[cfg.score_name] == -1:
                feature_vector = np.array([.4, .4,
                                           whois_importance["date"],
                                           whois_importance["exp_date"], whois_importance["country"],
                                           whois_importance["name"], suffix_features["importance_weight"],
                                           domain_data_importance["malicious_importance"],
                                           domain_data_importance["media_type_importance"]])
                # Compute Trustworthiness
                neo4j_features[cfg.score_name], normalized_importance = self.neo4j_connector.compute_trustworthiness_score(
                    feature_vector=feature_vector,
                    importance_matrix=importance_matrix,
                    weights=weights)
            else:
                feature_vector = np.array([neo4j_features[cfg.centrality_rank_name],
                                           neo4j_features[cfg.anonymous_rank_name],
                                           whois_importance["date"], whois_importance["exp_date"],
                                           whois_importance["country"],
                                           whois_importance["name"], suffix_features["importance_weight"],
                                           domain_data_importance["malicious_importance"],
                                           domain_data_importance["media_type_importance"]])
                normalized_importance = self.neo4j_connector.importance_weights_normalized(feature_vector,
                                                                                           importance_matrix)
            response.update({"neo4j_features": neo4j_features})

            # ==========================================================================================================
            # 1) Update centrality rank importance
            response["neo4j_features"]["centrality_rank_importance"] = np.round(normalized_importance[0][0],3)
            response["neo4j_features"]["centrality_rank"] = np.round(feature_vector[0], 3)
            # 2) Update centrality rank importance
            response["neo4j_features"]["anonymous_rank_importance"] = np.round(normalized_importance[1][0],3)
            response["neo4j_features"]["anonymous_rank"] = np.round(feature_vector[1], 3)
            # 3) Update creation date importance
            response["whois_importance"]["date_importance"] = np.round(normalized_importance[2][0],3)
            # 4) Update expiration date importance
            response["whois_importance"]["exp_date_importance"] = np.round(normalized_importance[3][0],3)
            # 5) Update country importance
            response["whois_importance"]["country_importance"] = np.round(normalized_importance[4][0],3)
            # 6) Update name importance
            response["whois_importance"]["name_importance"] = np.round(normalized_importance[5][0],3)
            # 7) Update suffix importance
            response["suffix_information"]["importance_weight"] = np.round(normalized_importance[6][0],3)
            # 8) Update domain_importance
            response["malicious_importance"] = np.round(normalized_importance[7][0],3)
            # 9) Update domain_importance
            response["media_type_importance"] = np.round(normalized_importance[8][0], 3)
            # ==========================================================================================================
            cfg.logger.info("Done! ")
        except Exception as e:
            cfg.logger.error(e)
        return response