import requests
import tweepy as tw
import pandas as pd
import numpy as np
import hiscore
import tldextract
from datetime import datetime
from helper import config as cfg
from helper.helper import (sigmoid, read_tld_data, extract_country_tld_weight,
                           extract_domain_from_url, read_csv_file,get_suffix_importance,
                           extract_domain_info_from_df, extract_publisher_info,
                           get_default_importance, media_type_importance,
                           get_current_timestamp, compare_timestamps, check_datetime_threshold)
from managers.neo4j_queries import Neo4jQueries
from managers.neo4j_connector import NEO4JConnector


# =======================================================================
# Twitter Data
consumer_key = "WcIJMyBF3spFEtRGHwqDlAKDT"
consumer_secret = "IfNlsgNrW5o6rfhayOURF1BcUDBcsrfgqss9g5inqeFytDbkgE"
access_token = "973174862159253505-mAYpqjzegRXFNhdEPXOkDLsHWXePp7q"
access_token_secret = "0mmfQcNDJBIFhMM9bexZSO1eIKhFdaP8JX9cMnBG81gJE"
# =======================================================================


def connect_twitter():
    try:
        cfg.logger.info("Connecting to Twitter API ... ")
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,
                     retry_count=10, retry_delay=5, retry_errors=5)
    except Exception as e:
        cfg.logger.error(e)
        api = None
    return api


# Collect tweets
def collect_tweets(api, search_words, date_since, items=1000, lang='en'):
    try:
        # Collect tweets
        tweets = tw.Cursor(api.search,
                           lang=lang,
                           q=(search_words),
                           since=date_since,
                           include_entities=True,
                           monitor_rate_limit=True,
                           wait_on_rate_limit=True,
                           tweet_mode='extended').items(items)
    except Exception as e:
        cfg.logger.error(e)
        tweets = None
    return tweets


def get_user_by_username(api, username):
    item = None
    try:
        user_items = api.search_users(username)
        item = user_items[0]
    except Exception as e:
        cfg.logger.error(e)
    return item


def get_user_data(user):
    user_data = None
    try:
        user_data = {"id": user.id, "id_str": user.id_str, "screen_name": user.screen_name,
                     "name": user.name, "followers_count": user.followers_count,
                     "friends_count": user.friends_count, "favourites_count": user.favourites_count,
                     "statuses_count": user.statuses_count, "location": user.location,
                     "created_at": user.created_at, "verified": user.verified,
                     "url": user.url, "description": user.description,
                     "protected": user.protected, "profile_banner_url": user.profile_banner_url,
                     "profile_image_url_https": user.profile_image_url_https
                     }
    except Exception as e:
        cfg.logger.error(e)
    return user_data


def get_average_tweets_per_day(created_date, statuses_count):
    avg_daily_tweets = -1
    try:
        delta = datetime.utcnow() - created_date
        account_age_days = delta.days
        if account_age_days > 0:
            avg_daily_tweets = (float(statuses_count) / float(account_age_days))
    except Exception as e:
        cfg.logger.error(e)
    return avg_daily_tweets


def compute_social_popularity(followers_count, friends_count):
    social_pop = -1
    try:
        if (followers_count > 0) and (friends_count > 0):
            social_pop = round(np.log(followers_count) - np.log(friends_count), 2)
    except Exception as e:
        cfg.logger.error(e)
    return social_pop


def compute_verification_score(verified, location):
    verification_score = np.tanh(-1)
    try:
        if verified:
            verification_score = np.tanh(1)
        if len(location):
            verification_score += np.tanh(1)
    except Exception as e:
        cfg.logger.error(e)
    return verification_score


def extract_user_features(user):
    user_features = None
    try:
        user_data = get_user_data(user)

        # Activity measurement
        avg_daily_tweets = get_average_tweets_per_day(created_date=user_data["created_at"],
                                                      statuses_count=user_data["statuses_count"])
        # Social influence
        social_pop = compute_social_popularity(followers_count=user_data["followers_count"],
                                               friends_count=user_data["friends_count"])
        # Verification
        verification_score = compute_verification_score(verified=user_data["verified"],
                                                        location=user_data["location"])
        # Get features
        user_features = {"activity_metric": avg_daily_tweets, "popularity_metric": social_pop,
                         "verification_metric": verification_score}
    except Exception as e:
        cfg.logger.error(e)
    return user_features


def generate_twitter_scorer(minval=0, maxval=100):
    score_func = None
    try:
        """  monotone_relationship -- A length-N vector with +1/-1 entries. +1
         indicates scores should be increasing in that attribute, -1 decreasing.

         | activity |   popularity  |   verification | score
         # -----------------------------------------------
         |    -1    |       -1      |    np.tanh(-1) |  0
         |    -1    |       -1      |    np.tanh(1)  |  5
         |    -1    |       -1      |    2*np.tanh(-1) |  10
         # -----------------------------------------------
         |    -1    |       5      |    np.tanh(-1) |  15
         |    -1    |       5      |    np.tanh(1)  |  20
         |    -1    |       5      |    2*np.tanh(-1) | 25
         # -----------------------------------------------
         |    -1    |       10      |    np.tanh(-1) |  30
         |    -1    |       10     |    np.tanh(1)  |  35
         |    -1    |       10      |    2*np.tanh(-1) |  40
         # -----------------------------------------------
         |    -1    |       15      |    np.tanh(-1) |  45
         |    -1    |       15     |    np.tanh(1)  |  50
         |    -1    |       15      |    2*np.tanh(-1) |  55
         -
         # -----------------------------------------------
         |    10    |       5      |    np.tanh(-1) |  60
         |    50    |       5      |    np.tanh(1)  |  65
         |    100    |       5      |    2*np.tanh(-1) | 70
         # -----------------------------------------------
         |    10    |       10      |    np.tanh(-1) |  75
         |    50    |       10     |    np.tanh(1)  |  80
         |    100    |       10      |    2*np.tanh(-1) |  85
         # -----------------------------------------------
         |    10    |       15      |    np.tanh(-1) |  90
         |    50    |       15     |    np.tanh(1)  |  95
         |    100    |       15      |    2*np.tanh(-1) |  100


         """
        reference_set = {(-1, -1, np.tanh(-1)): 0, (-1, -1, np.tanh(1)): 5, (-1, -1, 2 * np.tanh(1)): 10,
                         (-1, 3, np.tanh(-1)): 15, (-1, 3, np.tanh(1)): 20, (-1, 3, 2 * np.tanh(1)): 25,
                         (-1, 5, np.tanh(-1)): 30, (-1, 5, np.tanh(1)): 35, (-1, 5, 2 * np.tanh(1)): 40,
                         (-1, 10, np.tanh(-1)): 45, (-1, 10, np.tanh(1)): 50, (-1, 10, 2 * np.tanh(1)): 55,
                         (10, 3, np.tanh(-1)): 60, (50, 3, np.tanh(1)): 65, (100, 3, 2 * np.tanh(1)): 70,
                         (10, 5, np.tanh(-1)): 75, (50, 5, np.tanh(1)): 80, (100, 5, 2 * np.tanh(1)): 85,
                         (10, 10, np.tanh(-1)): 90, (50, 10, np.tanh(1)): 95, (100, 10, 2 * np.tanh(1)): 100,
                         }
        score_func = hiscore.create(reference_set, [1, 1, 1], minval=minval, maxval=maxval)

    except Exception as e:
        cfg.logger.error(e)
    return score_func

def compute_twitter_score(api, username, score_func):
    score = -1
    try:
        user = get_user_by_username(api, username)
        user_features = extract_user_features(user)

        score = np.round(score_func.calculate([(user_features["activity_metric"],
                                                user_features["popularity_metric"],
                                                user_features["verification_metric"])])).tolist()[0]
        # TODO: ADD RELEVANCE METRIC BASED ON THE DATE
    except Exception as e:
        cfg.logger.error(e)
    return score

def get_open_page_rank(source_domain):
    data = None
    try:
        API_KEY = "4ss0ow0kw4ok8cssks8g0gc8gcscso0o8w48o0o0"
        HEADERS = {"API-OPR": API_KEY}
        URL = "https://openpagerank.com/api/v1.0/getPageRank"
        PARAMS = {"domains[]": source_domain}
        response = requests.get(url=URL, params=PARAMS, headers=HEADERS)
        data = response.json()["response"][0]
    except Exception as e:
        print(e)
    return data

def compute_openrank_score(source_domain, label="page_rank_decimal"):
    score = -1
    try:
        response = get_open_page_rank(source_domain)
        page_rank = response[label]
        score = round(100*sigmoid(np.log(2) * np.log(page_rank)),2)
    except Exception as e:
        print(e)
    return score

def compute_suffix_score(domain, sheet_names, filepath, key="importance_weight"):
    suffix_vector = {"suffix": "", key: get_default_importance(), "additional_data": {}}
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
        tld_data[sheet_names[1]][key] = get_suffix_importance()

        # Get the suffix importance
        country_res = tld_data[sheet_names[0]].loc[tld_data[sheet_names[0]]['Name'] == suffix].to_dict()
        if country_res[key]:
            suffix_vector[key] = list(country_res[key].values())[0]
            values = [list(country_res[kk].values())[0] for kk in country_res]
            keys = list(country_res.keys())
            suffix_vector["additional_data"] = dict(zip(keys, values))
            suffix_vector["additional_data"]["Administrator"] = get_default_importance()
        else:
            orig_res = tld_data[sheet_names[1]].loc[tld_data[sheet_names[1]]['Name'] == suffix].to_dict()
            if orig_res[key]:
                suffix_vector[key] = list(orig_res[key].values())[0]
                values = [list(orig_res[kk].values())[0] for kk in orig_res]
                keys = list(orig_res.keys())
                suffix_vector["additional_data"] = dict(zip(keys, values))
            else:
                suffix_vector[key] = get_default_importance()
                suffix_vector["additional_data"] = {}

        # Update keys
        keys = list(suffix_vector["additional_data"].keys())
        keys = [kk.lower() for kk in keys]
        values = list(suffix_vector["additional_data"].values())
        suffix_vector["additional_data"] = dict(zip(keys, values))

    except Exception as e:
        cfg.logger.error(e)
    return suffix_vector


def get_publisher_score(graph, uuid, label_a, label_b, relationship):
    publisher_score = -1
    try:
        query = Neo4jQueries.get_nodes_by_relationship(label_a, label_b, relationship,
                                                       uuid, uuid_label="identifier")
        response = NEO4JConnector.get_data_from_query(graph=graph, query=query)

        if response is not None and len(response) > 0:
            pub_scores = []
            for res in response:
                pub_scores.append(float(res["publisher"]["trustworthiness"]))
            publisher_score = np.median(pub_scores).tolist()
        # Normalize value
        publisher_score = round(publisher_score, 2)
    except Exception as e:
        cfg.logger.error(e)
    return publisher_score

def compute_text_score(es, graph, uuid, label_a, label_b, relationship, art_index, relevance, alpha=.20):
    text_score = -1
    try:
        query = Neo4jQueries.get_nodes_ids_by_relationship(label_a, label_b, relationship,
                                                            uuid, uuid_label="identifier")
        response = NEO4JConnector.get_data_from_query(graph=graph, query=query)

        # It retrieves several articles
        text_trust = []
        if len(response)>0:
            for res in response:
                art_uuid = res["Identifiers"]
                # Retrieve article from Elasticsearch
                art_obj = es.retrieve_data_from_index_by_searching(
                    index=art_index, search_key="identifier", search_value=art_uuid,
                    fuzzy_threshold=99, request_timeout=30)
                # Append Trustworthiness
                text_trust.append(check_text_score(art_obj, relevance, alpha))
        if text_trust:
            text_score = np.median(text_trust).tolist()
        else:
            text_score = float(0)
        # Normalize score
        text_score = round(text_score, 2)
    except Exception as e:
        cfg.logger.error(e)
    return text_score

def check_text_score(art_obj, relevance, alpha=.20):
    norm_relevance = 0.5
    try:
        norm_relevance = relevance_mapping(x=relevance, alpha=alpha)
        text_score = (100*float(art_obj["source"]["calculatedRatingDetail"]["textRating"]))*norm_relevance
    except Exception as e:
        cfg.logger.warning("TextRating not available yet!")
        text_score = 50*norm_relevance
    return text_score

def compute_centrality_rank(graph, label, uuid, uuid_label, relationship, default_controller=0.63):
    centrality_rank = -1
    try:
        query_art_rank = Neo4jQueries.create_rank_query(algorithm="articleRank",
                                                        label=label,
                                                        relationship=relationship,
                                                        damping_factor=default_controller,
                                                        uuid=uuid_label)

        query_eigen_rank = Neo4jQueries.create_rank_query(algorithm="eigenvector",
                                                          label=label,
                                                          relationship=relationship,
                                                          damping_factor=default_controller,
                                                          uuid=uuid_label)

        art_rank = compute_rank_algorithm(uuid=uuid, graph=graph, query=query_art_rank,
                                          default_controller=default_controller)
        eigen_rank = compute_rank_algorithm(uuid=uuid, graph=graph, query=query_eigen_rank,
                                            default_controller=default_controller)
        centrality_rank = art_rank + eigen_rank
    except Exception as e:
        cfg.logger.error(e)
    return centrality_rank


def get_object_in_graph(graph, label, property_label, property):
    object_data = {}
    try:
        query_obj = Neo4jQueries.get_node_by_property(label, property_label, property)
        response = NEO4JConnector.get_data_from_query(graph=graph, query=query_obj)
        if response is not None and len(response) > 0:
            object_data = dict(response[0]["data"])
    except Exception as e:
        cfg.logger.error(e)
    return object_data

def check_twitter_analysis_date(graph, label, property_label, property):
    response = {"analyse": False, "score": -1}
    try:
        # Get object from graph
        obj_data = get_object_in_graph(graph, label, property_label, property)
        t2 = get_current_timestamp()
        # There is an object
        if obj_data:
            if "processed_timestamp" in list(obj_data.keys()) and "twitter_rank" in list(obj_data.keys()):
                t1 = float(obj_data["processed_timestamp"])
                # Get specific keys from object
                dt_diff = compare_timestamps(t1, t2)
                response["analyse"] = check_datetime_threshold(dt_diff, threshold=7)
            else:
                response["analyse"] = True
                # SET PROPERTY
                query_set_prop = Neo4jQueries.set_property_to_node(label=
                                                                   label,
                                                                   uuid_label=property_label,
                                                                   uuid=property,
                                                                   property="processed_timestamp",
                                                                   value=str(t2))
                NEO4JConnector.run_query(graph, query=query_set_prop)

        if not response["analyse"]:
            response["score"] = float(obj_data["twitter_rank"])

    except Exception as e:
        cfg.logger.info(e)
    return response


def compute_article_rank(graph, label_a, label_b, uuid, relationship, uuid_label="identifier"):
    article_rank = -1
    try:
        query_total = Neo4jQueries.get_total_nodes_by_relationship(label_a=label_a,
                                                                   label_b=label_b,
                                                                   relationship=relationship,
                                                                   uuid=uuid,
                                                                   uuid_label=uuid_label)
        response = NEO4JConnector.get_data_from_query(graph=graph, query=query_total)
        if response is not None and len(response) > 0:
            article_rank = response[0]["Total"]

    except Exception as e:
        cfg.logger.error(e)
    return article_rank

def compute_rank_algorithm(uuid, graph, query, default_controller=0.15, label="publisher"):
    rank_score = default_controller
    try:
        query_el = Neo4jQueries.count_nodes_same_label(label=label.title())
        n_elements = NEO4JConnector.get_data_from_query(graph=graph, query=query_el)
        if n_elements[0]["total"] >= 2:
            try:
                rank = NEO4JConnector.get_data_from_query(graph=graph, query=query)
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

def compute_domain_importance(domain_data):
    return media_type_importance(domain_data)


def collect_domain_info_from_db(full_domain, csv_filepath):
    domain_data = {"location": cfg.org_default_field,
                   "media_type": cfg.org_default_field,
                   "media_focus": cfg.org_default_field,
                   "language": [],
                   "platform": []}
    domain = None
    df_websites = None
    try:
        # Retrieve domain
        domain_info = extract_domain_from_url(full_domain)
        registered_domain = domain_info.registered_domain
        domain = domain_info.domain
        df_websites = read_csv_file(csv_filepath)
        df_websites = df_websites.fillna("N/A", inplace=False)
        domain_data = extract_domain_info_from_df(df_websites, registered_domain, full_domain)
    except Exception as e:
        cfg.logger.error(e)
    return domain, df_websites, domain_data


def compute_media_type_score(full_domain, csv_filepath):
    score = -1
    try:
        domain, df_websites, domain_data = collect_domain_info_from_db(full_domain, csv_filepath)
        domain_importance = compute_domain_importance(domain_data)
        score = domain_importance["media_type_importance"]
    except Exception as e:
        cfg.logger.error(e)
    return score

def extract_information_from_domain(domain, default_field="N/A",  list_of_websites=None):
    whois_features = {}
    try:
        whois_features = extract_publisher_info(source_domain=domain, list_of_websites=list_of_websites,
                                                threshold=95, default_str=default_field)
    except Exception as e:
        cfg.logger.error(e)
    return whois_features

def relevance_mapping(x, alpha=.20):
    return 1- (1/(1+alpha*x))

def retrieve_authors_associated_to_publisher(graph, label_a, label_b, relationship, publisher_uuid,
                                             authors_done=None, columns=None):
    remain_authors = pd.DataFrame(columns=columns)
    author_data = []
    try:
        query_el = Neo4jQueries.get_nodes_by_relationship_opposite(label_a, label_b, relationship,
                                                                   publisher_uuid, uuid_label="identifier")
        response = NEO4JConnector.get_data_from_query(graph=graph, query=query_el)

        if len(response) > 0:
            # Remove authors tha were already analysed
            if authors_done is not None:
                author_data = [dict(i["data"]) for i in response if i["data"]["identifier"] not in authors_done]
            else:
                author_data = [dict(i["data"]) for i in response]
        if author_data:
            remain_authors = pd.DataFrame(author_data)
            remain_authors = remain_authors[columns]
    except Exception as e:
        cfg.logger.error(e)
    return remain_authors

def get_data_from_neo4j(graph, label, uuid):
    output_neo4j = None
    try:
        columns = ["trustworthiness", "page_rank", "suffix_rank", "text_rank", "twitter_rank", "media_type_rank"]
        query_data = Neo4jQueries.get_node_by_property(label=label, property=uuid,
                                                       property_label="identifier")
        response = NEO4JConnector.get_data_from_query(graph, query_data)
        if len(response) > 0:
            output_data = dict(response[0]["data"])
            output_data_df = pd.DataFrame(output_data, index=[0])
            non_output_neo4j = output_data_df[columns].to_dict()
            output_neo4j = {}
            for k,v in non_output_neo4j.items():
                output_neo4j[k] = round(float(non_output_neo4j[k][0]),2)
    except Exception as e:
        cfg.logger.error(e)
    return output_neo4j