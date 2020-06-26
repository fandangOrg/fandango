from fuzzywuzzy import fuzz
import numpy as np
import pytz
import requests
import pycountry
import whois
import tldextract
import codecs
import re
import favicon
import pandas as pd
from pysafebrowsing import SafeBrowsing
from helper import global_variables as gv
from difflib import SequenceMatcher
from restcountries import RestCountryApiV2 as rapi
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from scipy import stats


def get_country_by_code(country_code):
    try:
        country_domain = get_countries_domains()
        country = country_domain[country_code]
    except Exception as e:
        gv.logger.warning(e)
        country = "Not Specified"
    return country


def get_datetime():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S %z")
    return date_time


def extract_publisher_info(source_domain, list_of_websites=None, threshold=95, default_str="Unknown"):
    required_fields = {"domain_name", "creation_date", "expiration_date", "status", "name", "org",
                       "city", "state", "zipcode", "country", "suffix", "whois_name", "whois_country",
                       "nationality"}
    source_domain_data = dict(zip(list(required_fields), [gv.org_default_field for i in range(len(required_fields))]))

    try:
        # WhoisIP
        ttd = tldextract.extract(source_domain)
        w = whois.whois(source_domain)
        # To dict
        source_domain_data = dict(w)

        # Not all the required information is available
        if not source_domain_data.keys() >= required_fields:
            # 1) Domain name
            if "domain_name" not in source_domain_data.keys():
                source_domain_data["domain_name"] = None
            else:
                if isinstance(source_domain_data["domain_name"], list):
                    source_domain_data["domain_name"] = source_domain_data["domain_name"][0].lower()

            # 2) Creation date
            if "creation_date" not in source_domain_data.keys():
                source_domain_data["creation_date"] = gv.org_default_field
            else:
                if isinstance(source_domain_data["creation_date"], list):
                    source_domain_data["creation_date"] = source_domain_data["creation_date"][0]
                # Add time zone utc
                if isinstance(source_domain_data["creation_date"], datetime):
                    d = pytz.UTC.localize(source_domain_data["creation_date"])
                    source_domain_data["creation_date"] = d.strftime("%Y-%m-%d %H:%M:%S %Z")
                if source_domain_data["creation_date"] is None:
                    source_domain_data["creation_date"] = gv.org_default_field

            # 3) Expiration date
            if "expiration_date" not in source_domain_data.keys():
                source_domain_data["expiration_date"] = gv.org_default_field
            else:
                if isinstance(source_domain_data["expiration_date"], list):
                    source_domain_data["expiration_date"] = source_domain_data["expiration_date"][0]
                # Add time zone utc
                if isinstance(source_domain_data["expiration_date"], datetime):
                    d = pytz.UTC.localize(source_domain_data["expiration_date"])
                    source_domain_data["expiration_date"] = d.strftime("%Y-%m-%d %H:%M:%S %Z")
                if source_domain_data["expiration_date"] is None:
                    source_domain_data["expiration_date"] = gv.org_default_field

            # 4) Updated date
            if "updated_date" not in source_domain_data.keys():
                source_domain_data["updated_date"] = gv.org_default_field
            else:
                if isinstance(source_domain_data["updated_date"], list):
                    source_domain_data["updated_date"] = source_domain_data["updated_date"][0]
                # Add time zone utc
                if isinstance(source_domain_data["updated_date"], datetime):
                    d = pytz.UTC.localize(source_domain_data["updated_date"])
                    source_domain_data["updated_date"] = d.strftime("%Y-%m-%d %H:%M:%S %Z")
                if source_domain_data["updated_date"] is None:
                    source_domain_data["updated_date"] = gv.org_default_field

            # 5) String keys
            standard_keys = ["status", "name", "org", "city", "state", "zipcode"]
            for i in standard_keys:
                if i not in source_domain_data.keys():
                    source_domain_data[i] = gv.org_default_field
                elif i in source_domain_data.keys() and source_domain_data[i] is not None:
                    if isinstance(source_domain_data[i] , list):
                        source_domain_data[i] = source_domain_data[i][0]
                    source_domain_data[i] = str(source_domain_data[i])
                else:
                    source_domain_data[i] = gv.org_default_field

            # 6) Extract source domain information

            if source_domain_data["domain_name"] is None:
                # tldExtractor
                source_domain_data["domain_name"] = ttd.registered_domain

            # Add a new key for whois name
            source_domain_data["whois_name"] = source_domain_data["name"]

            if list_of_websites is not None:
                source_domain_data["name"] = check_name_publisher(publisher_name=ttd.domain.lower(),
                                                                  organizations_list=list_of_websites,
                                                                  threshold=threshold)
            else:
                source_domain_data["name"] = ttd.domain.upper()
            source_domain_data["suffix"] = ttd.suffix

            # 7) Country and nationality
            if 'country' in source_domain_data.keys() and source_domain_data['country'] is not None:
                country_code = source_domain_data['country']
                country_data = pycountry.countries.get(alpha_2=country_code.upper())
                if country_data is not None:
                    source_domain_data['whois_country'] = str(country_data.official_name)
                else:
                    try:
                        source_domain_data['whois_country'] = gv.country_domains[country_code.lower()]
                    except Exception as e:
                        source_domain_data['whois_country'] = gv.org_default_field
                        country_data = None
                    # Try to match with countries data
            else:
                country_data = None
                source_domain_data['whois_country'] = gv.org_default_field

            if country_data is None:
                country_code = str(ttd.suffix) #source_domain.split('.')[-1]
                try:
                    source_domain_data['country'] = str(pycountry.countries.get(alpha_2=country_code.upper()).official_name)

                except Exception as e:
                    try:
                        source_domain_data['country'] = gv.country_domains[country_code.lower()]
                    except Exception as e:
                        source_domain_data['country'] = gv.org_default_field
            else:
                source_domain_data['country'] = str(country_data.official_name)

        try:
            source_domain_data["nationality"] = rapi.get_countries_by_name(source_domain_data['country'])[0].demonym
        except Exception as e:
            try:
                source_domain_data["nationality"] = rapi.get_countries_by_name(source_domain_data['whois_country'])[0].demonym
            except Exception as e:
                source_domain_data["nationality"] = gv.org_default_field

                # Only keep the required keys
        source_domain_data = dict((key,value) for key, value in source_domain_data.items() if key in list(required_fields))

        # Replace None values
        source_domain_data = replace_none_with_empty_str(data_dict=source_domain_data,default_str=default_str)
    except Exception as e:
        gv.logger.error(e)
    return source_domain_data


def check_name_publisher(publisher_name, organizations_list, threshold=95):
    publisher_name_cleaned = None
    try:
        if isinstance(organizations_list, pd.DataFrame):
            organizations_list = organizations_list["name"].values.tolist()

        similarity = []
        org_lower = [org.replace(' ', '').lower() for org in organizations_list]
        # Compute similarity
        for i, org in enumerate(org_lower):
            similarity.append(fuzz.ratio(org, publisher_name.lower()))
        if np.max(similarity) > threshold:
            idx = np.argmax(np.array(similarity))
            publisher_name_cleaned = organizations_list[idx]
        else:
            publisher_name_cleaned = publisher_name.upper()
    except Exception as e:
        gv.logger.error(e)
    return publisher_name_cleaned


def remove_duplicate_strings_from_list(str_lst, min_char=3, fuzzy=False, fuzzy_threshold=.8):
    unique_str_lst = str_lst
    try:
        if len(str_lst) > 0:
            str_lst = [i for i in str_lst if i is not None and len(i) >= min_char]
            if len(str_lst) > 0:
                if not fuzzy:
                    unique_str_lst = list(set(str_lst))
                else:
                    unique_str_lst = fuzzy_similarity_search(data=str_lst, threshold=fuzzy_threshold)
            else:
                unique_str_lst = [gv.default_field]
        else:
            unique_str_lst = [gv.default_field]
    except Exception as e:
        gv.logger.error(e)
    return unique_str_lst


def fuzzy_similarity_search(data, threshold=.8):
    new_data = []
    try:
        for i, val in enumerate(data):
            # First iteration
            if i == 0:
                new_data.append(val)
            else:
                index_ls = []
                for j, val_new in enumerate(new_data):
                    dist = SequenceMatcher(None, val, val_new).ratio()
                    if dist >= threshold:
                        insert = False
                    else:
                        insert = True
                    index_ls.append(insert)

                if False not in index_ls:
                    new_data.append(val)

    except Exception as e:
        gv.logger.error(e)
    return new_data


def create_websites_db(filepath, countries):
    df = pd.DataFrame()
    try:
        for cont in countries:
            gv.logger.info("Extracting data from %s", cont)
            df_temp = pd.read_excel(filepath, sheet_name=cont, skip_blank_lines=False)
            cols = list(df_temp.columns)
            moDf = df_temp.dropna(how='any', subset=cols[1:4])

            # Replace nans by unknown
            moDf = moDf.fillna("N/A")
            df = pd.concat([df, moDf], axis=0)
    except Exception as e:
        gv.logger.error(e)
    return df

def read_csv_file(filepath):
    df = None
    try:
        df = pd.read_csv(filepath, index_col=0)
    except Exception as e:
        gv.logger.error(e)
    return df

def create_csv_from_df(df, filepath):
    try:
        df.to_csv(filepath)
    except Exception as e:
        gv.logger.error(e)


def normalize_value(mu: float = 50, sigma: float = 2):
    normalize_val: float = mu
    try:
        normalize_val: float = np.round(np.random.normal(mu, sigma, 1)[0], 3)
    except Exception as e:
        gv.logger.error(e)
    return normalize_val


def read_tld_data(filepath, sheet_names):
    df_data = {}
    try:
        for i in range(len(sheet_names)):
            df_tld = pd.read_excel(filepath, sheet_name=i, skip_blank_lines=False)
            df_tld.fillna("N/A", inplace=True)
            df_tld.replace("Unknown", "N/A", inplace=True)
            df_data[sheet_names[i]] = df_tld
    except Exception as e:
        gv.logger.error(e)
    return df_data


def get_suffix_importance():
    # com ||org ||net ||int || edu ||gov || mil
    return np.round(100*np.array([2*stats.norm.pdf(1), 2*stats.norm.pdf(0),
            2*stats.norm.pdf(3), 2*stats.norm.pdf(2),
            2*stats.norm.pdf(0), 2*stats.norm.pdf(0),
            2*stats.norm.pdf(1)]),2)

def media_type_importance(domain_data):
    domain_importance = {"media_type_importance": 2*stats.norm.pdf(1.5),
                         "malicious_importance": 2*stats.norm.pdf(1.5) }
    try:
        # Malicious
        if domain_data["malicious"]:
            importance_malicius = 2*stats.norm.pdf(1.5)
        else:
            importance_malicius = 2*stats.norm.pdf(3)

        if domain_data["media_type"] == "Broadcast" or domain_data["media_type"] == "Press Agency":
            importance = 2*stats.norm.pdf(0)
        elif domain_data["media_type"] == "Newspaper":
            importance= 2*stats.norm.pdf(0.20)
        elif domain_data["media_type"] == "Magazine":
            importance = 2*stats.norm.pdf(1.5)
        else:
            importance = 2*stats.norm.pdf(2)

        domain_importance["media_type_importance"] = np.round(100*importance, 2)
        domain_importance["malicious_importance"] = np.round(100*importance_malicius, 2)
    except Exception as e:
        gv.logger.error(e)
    return domain_importance

def extract_country_tld_weight(row):
    total_weight = 0
    try:
        importance_weights = {"Yes": 0.25, "No": 0,
                              "N/A": 0}
        dnssec = row["DNSSEC"]
        idn = row["IDN"]
        ipv6 = row["IPv6"]
        sld = row["SLD"]

        if dnssec in importance_weights:
            total_weight = importance_weights[dnssec]
        if idn in importance_weights:
            total_weight += importance_weights[idn]
        if ipv6 in importance_weights:
            total_weight += importance_weights[ipv6]
        if sld in importance_weights:
            total_weight += importance_weights[sld]

        total_weight = np.round(100*total_weight, 2)
    except Exception as e:
        gv.logger.error(e)
    return total_weight

def get_default_importance():
    return round(100*(2*stats.norm.pdf(2)),2 )

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def get_datetime_from_str(str_date):
    try:
        date_obj = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S UTC')
    except Exception as e:
        gv.logger.warning(e)
        date_obj = None
    return date_obj


def get_distance_between_dates(start_date, end_date, time="years"):
    difference = -1
    try:
        difference = relativedelta(start_date, end_date)
        if time == "years":
            difference = difference.years
        elif time == "months":
            difference = diff_month(d1=start_date, d2=end_date)
        else:
            difference = difference.years
    except Exception as e:
        gv.logger.error(e)
    return difference


def sigmoid(x, derivative=False):
  return x*(1-x) if derivative else 1/(1+np.exp(-x))


def normalize_trustworthiness(score: float):
    trustworthiness: float = score
    try:
        trustworthiness = round(score, 2)
        if trustworthiness <= 0:
            trustworthiness = normalize_value(mu=5, sigma=1)
        elif trustworthiness >= 100:
            trustworthiness = normalize_value(mu=95, sigma=1)
    except Exception as e:
        gv.logger.error(e)
    return trustworthiness


def change_importance(data, key, importance_data, new_importance=0):
    importance_data_ls = []
    try:
        # -------------------------------------------------------
        idx = list(data.keys()).index(key)
        importance_data_ls = list(importance_data)
        importance_data_ls[idx] = float(new_importance)
        # -------------------------------------------------------
    except Exception as e:
        gv.logger.error(e)
    return importance_data_ls


def join_dict_from_nested_list(nested_dict, ls1_id, ls2_id):
    data_dict = None
    try:
        n_elements = len(nested_dict[ls1_id])
        keys = [ls1_id] + list(nested_dict[ls2_id][0].keys())
        values = [[] for i in range(len(keys))]
        data_dict = dict(zip(keys, values))

        for i in range(n_elements):
            data_dict[ls1_id].append(nested_dict[ls1_id][i])
            for k, v in nested_dict[ls2_id][i].items():
                data_dict[k].append(nested_dict[ls2_id][i][k])
    except Exception as e:
        gv.logger.error(e)
    return data_dict


def replace_none_with_empty_str(data_dict, default_str):
    return {k: (default_str if v is None else v) for k, v in data_dict.items() }


def extract_media_information(output_rows):
    media_info = {}
    try:
        information_keys = ["Media Type", "Media Focus", "Language"]
        for i in output_rows:
            for j in i:
                if j[0] in information_keys:
                    main_key = '_'.join(j[0].lower().split(" "))
                    partial_dict = {main_key:{}}
                    for d in j[1:]:
                        key_val_data = d.split("-")
                        info_partial_dict = {key_val_data[0]: key_val_data[1]}
                        partial_dict[main_key].update(info_partial_dict)
                    media_info.update(partial_dict)
    except Exception as e:
        gv.logger.error(e)
    return media_info


def extract_tables_from_html(html_link, local=True):
    output_rows, output_links = None, None
    try:
        if not local:
            response = requests.get(html_link, timeout=10)
            # HTML Content
            content = str(response.content)
            soup = BeautifulSoup(content, 'lxml')
            split_by = "\\n"
        else:
            soup = BeautifulSoup(open(html_link), "lxml")
            split_by = "\n"
        # Extract all tags
        tables = soup.findAll("table")
        output_rows = []
        output_links = []

        for index, table in enumerate(tables):
            if index == 17:
                ss = 2
            for table_row in table.findAll('tr'):
                columns = table_row.findAll('td')
                links = table_row.findAll('a', attrs={'href': re.compile("^(http|https)://")})
                output_links.append(list(links))
                output_row = []
                for i_c, column in enumerate(columns):
                    text = column.text.split(split_by)
                    # Check links
                    #non_data_index = check_empty_field_list(text)
                    """if non_data_index:
                        text = [val for i, val in enumerate(text) if i not in non_data_index]"""
                    final_text = [codecs.decode(i, 'unicode_escape') for i in text]
                    # Check list
                    output_row.append(final_text)
                output_rows.append(output_row)
    except Exception as e:
        gv.logger.error(e)
    return (output_rows, output_links)


def analyze_url(urls):
    malicious_data = {}
    try:
        KEY = "AIzaSyDkOOAhXdZQdN1SPJ7QbPgVqcorSKtdtbE"
        s = SafeBrowsing(KEY)
        r = s.lookup_urls(urls)
        malicious_data = r[urls[0]]
    except Exception as e:
        gv.logger.error(e)
    return malicious_data


def extract_domain_info_from_df(df, domain, full_domain):
    domain_info_result = {"location": gv.org_default_field,
                          "media_type": gv.org_default_field,
                          "media_focus": gv.org_default_field,
                          "language": [],
                          "platform": []}
    try:
        domain_info = df.loc[df['domain_url'].isin([domain])].reset_index().to_dict()
        if domain_info["index"]:
            domain_info_result = {"location": domain_info["location"][0],
                                  "media_type": domain_info["media_type"][0],
                                  "media_focus": domain_info["media_focus"][0],
                                  "language": list(set(domain_info["language"].values())),
                                  "platform": list(set(domain_info["platform"].values()))}

        url_domain_retrieve = list(domain_info["domain"].values())
        if url_domain_retrieve:
            url_domain = url_domain_retrieve[0]
        else:
            url_domain = full_domain

        # Safe URL
        malicious_data = analyze_url([url_domain])
        domain_info_result.update(malicious_data)

        # Favicon
        icons = get_favicon(url=full_domain)
        domain_info_result.update({"favicon": icons})
    except Exception as e:
        gv.logger.error(e)
    return domain_info_result


def fuzzy_distance(str_1, str_2):
    similarity = -1
    try:
        similarity = fuzz.ratio(str_1.lower().strip().replace(" ", ""),
                                str_2.lower().strip().replace(" ", ""))
    except Exception as e:
        gv.logger.error(e)
    return similarity

def extract_domain_from_url(url):
    domain_info = None
    try:
        domain_info = tldextract.extract(url)
    except Exception as e:
        gv.logger.error(e)
    return domain_info

def add_protocol_to_domain(domain, protocol="http"):
    full_domain = None
    try:
        full_domain = protocol + "://" + domain + "/"
    except Exception as e:
        gv.logger.error(e)
    return full_domain


def get_favicon(url):
    icons = ""
    total_icons = []
    try:
        domain_info = tldextract.extract(url)
        fqdn = domain_info.fqdn
        domain_protocols = [add_protocol_to_domain(domain=fqdn),
                            add_protocol_to_domain(domain=fqdn, protocol="https")]
        for dom in domain_protocols:
            total_icons.append(favicon.get(dom)[0].url)
        if total_icons:
            icons = total_icons[0]
        else:
            icons = gv.logo_fandango
    except Exception as e:
        print(e)
    return icons


def get_weighted_average(data, weights):
    diag_dot = np.array([-1 for i in range(data.shape[0])])
    weighted_mean = -1
    try:
        if len(data.shape) > 1:
            data = data.ravel()
        diag_dot = np.dot(np.diag(data), weights)
        weighted_mean = np.sum(diag_dot) / np.sum(weights)
    except Exception as e:
        gv.logger.error(e)
    return weighted_mean, diag_dot


def retrieve_neo4j_features_from_db(filepath, domain):
    df = pd.read_excel(filepath, skip_blank_lines=False)
    data_neo4j = {"trustworthiness": -1,
                  "centrality_rank": .4,
                  "anonymous_rank": .4}
    try:
        domain_info = df.loc[df['url'].isin([domain])].reset_index().to_dict()
        if domain_info["index"]:
            if len(domain_info["trustworthiness"]) > 1:
                all_scores = list(domain_info["trustworthiness"].values())
                max_index = np.argmax(all_scores)
            else:
                max_index = 0
            data_neo4j = {"trustworthiness": domain_info["trustworthiness"][max_index],
                          "centrality_rank": domain_info["centrality_rank"][max_index],
                          "anonymous_rank": domain_info["anonymous_rank"][max_index]}
    except Exception as e:
        gv.logger.info(e)
    return data_neo4j


def merge_dataframes(df1, df2):
    df = None
    try:
        # Reset index
        df2 = df2.reset_index(drop=True)
        df = pd.concat([df1, df2], axis=0)
        df = df.reset_index(drop=True)
    except Exception as e:
        gv.logger.error(e)
    return df


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.__str__()
    raise TypeError ("Type %s not serializable" % type(obj))

def select_keys_from_dict(data, keys):
    data_obj = {}
    try:
        data_obj = dict((k, data[k]) for k in keys if k in data)
    except Exception as e:
        gv.logger.error(e)
    return data_obj

def get_current_timestamp():
    timestamp = ""
    try:
        current_time = datetime.now()
        timestamp = datetime.timestamp(current_time)
    except Exception as e:
        gv.logger.error(e)
    return timestamp

def compare_timestamps(t1:{float}, t2:{float}):
    dt_diff = -1
    try:
        dt1 = datetime.fromtimestamp(t1)
        dt2 = datetime.fromtimestamp(t2)
        dt_diff = abs(dt2 - dt1)
    except Exception as e:
        gv.logger.error(e)
    return dt_diff

def check_datetime_threshold(dt_diff:{timedelta}, threshold=7):
    response = False
    try:
        if dt_diff.days > threshold:
            response = True
    except Exception as e:
        gv.logger.error(e)
    return response

def get_countries_domains():
    country_domains = {}
    try:
        country_domains = {'ac': 'Ascension Island (UK)',
                           'ad': 'Andorra',
                           'ae': 'United Arab Emirates',
                           'af': 'Afghanistan',
                           'ag': 'Antigua and Barbuda',
                           'ai': 'Anguilla (UK)',
                           'al': 'Albania',
                           'am': 'Armenia',
                           'ao': 'Angola',
                           'ar': 'Argentina',
                           'as': 'American Samoa (USA)',
                           'at': 'Austria',
                           'au': 'Australia',
                           'aw': 'Aruba (Netherlands)',
                           'ax': 'Aland Islands (Finland)',
                           'az': 'Azerbaijan',
                           'ba': 'Bosnia and Herzegovina',
                           'bb': 'Barbados',
                           'bd': 'Bangladesh',
                           'be': 'Belgium',
                           'bf': 'Burkina Faso',
                           'bg': 'Bulgaria',
                           'bh': 'Bahrain',
                           'bi': 'Burundi',
                           'bj': 'Benin',
                           'bm': 'Bermuda (UK)',
                           'bn': 'Brunei',
                           'bo': 'Bolivia',
                           'br': 'Brazil',
                           'bs': 'Bahamas',
                           'bt': 'Bhutan',
                           'bv': 'Bouvet Island (Norway)',
                           'bw': 'Botswana',
                           'by': 'Belarus',
                           'bz': 'Belize',
                           'ca': 'Canada',
                           'cc': 'Cocos (Keeling) Islands (Australia)',
                           'cd': 'Democratic Republic of the Congo',
                           'cf': 'Central African Republic',
                           'cg': 'Republic of the Congo',
                           'ch': 'Switzerland',
                           'ci': 'Cote d\'Ivoire',
                           'ck': 'Cook Islands (New Zealand)',
                           'cl': 'Chile',
                           'cm': 'Cameroon',
                           'cn': 'China',
                           'co': 'Colombia',
                           'cr': 'Costa Rica',
                           'cu': 'Cuba',
                           'cv': 'Cabo Verde',
                           'cw': 'Curacao (Netherlands)',
                           'cx': 'Christmas Island (Australia)',
                           'cy': 'Cyprus',
                           'cz': 'Czechia',
                           'de': 'Germany',
                           'dj': 'Djibouti',
                           'dk': 'Denmark',
                           'dm': 'Dominica',
                           'do': 'Dominican Republic',
                           'dz': 'Algeria',
                           'ec': 'Ecuador',
                           'ee': 'Estonia',
                           'eg': 'Egypt',
                           'er': 'Eritrea',
                           'es': 'Spain',
                           'et': 'Ethiopia',
                           'eu': 'European Union',
                           'fi': 'Finland',
                           'fj': 'Fiji',
                           'fk': 'Falkland Islands (UK)',
                           'fm': 'Federated States of Micronesia',
                           'fo': 'Faroe Islands (Denmark)',
                           'fr': 'France',
                           'ga': 'Gabon',
                           'gb': 'United Kingdom',
                           'gd': 'Grenada',
                           'ge': 'Georgia',
                           'gf': 'French Guiana (France)',
                           'gg': 'Guernsey (UK)',
                           'gh': 'Ghana',
                           'gi': 'Gibraltar (UK)',
                           'gl': 'Greenland (Denmark)',
                           'gm': 'Gambia',
                           'gn': 'Guinea',
                           'gp': 'Guadeloupe (France)',
                           'gq': 'Equatorial Guinea',
                           'gr': 'Greece',
                           'gs': 'South Georgia and the South Sandwich Islands (UK)',
                           'gt': 'Guatemala',
                           'gu': 'Guam (USA)',
                           'gw': 'Guinea-Bissau',
                           'gy': 'Guyana',
                           'hk': 'Hong Kong (China)',
                           'hm': 'Heard Island and McDonald Islands (Australia)',
                           'hn': 'Honduras',
                           'hr': 'Croatia',
                           'ht': 'Haiti',
                           'hu': 'Hungary',
                           'id': 'Indonesia',
                           'ie': 'Ireland',
                           'il': 'Israel',
                           'im': 'Isle of Man (UK)',
                           'in': 'India',
                           'io': 'British Indian Ocean Territory (UK)',
                           'iq': 'Iraq',
                           'ir': 'Iran',
                           'is': 'Iceland',
                           'it': 'Italy',
                           'je': 'Jersey (UK)',
                           'jm': 'Jamaica',
                           'jo': 'Jordan',
                           'jp': 'Japan',
                           'ke': 'Kenya',
                           'kg': 'Kyrgyzstan',
                           'kh': 'Cambodia',
                           'ki': 'Kiribati',
                           'km': 'Comoros',
                           'kn': 'Saint Kitts and Nevis',
                           'kp': 'North Korea',
                           'kr': 'South Koreav',
                           'kw': 'Kuwait',
                           'ky': 'Cayman Islands (UK)',
                           'kz': 'Kazakhstan',
                           'la': 'Laos',
                           'lb': 'Lebanon',
                           'lc': 'Saint Lucia',
                           'li': 'Liechtenstein',
                           'lk': 'Sri Lanka',
                           'lr': 'Liberia',
                           'ls': 'Lesotho',
                           'lt': 'Lithuania',
                           'lu': 'Luxembourg',
                           'lv': 'Latvia',
                           'ly': 'Libya',
                           'ma': 'Morocco',
                           'mc': 'Monaco',
                           'md': 'Moldova',
                           'me': 'Montenegro',
                           'mg': 'Madagascar',
                           'mh': 'Marshall Islands',
                           'mk': 'North Macedonia (formerly Macedonia)',
                           'ml': 'Mali',
                           'mm': 'Myanmar (formerly Burma)',
                           'mn': 'Mongolia',
                           'mo': 'Macau (China)',
                           'mp': 'Northern Mariana Islands (USA)',
                           'mq': 'Martinique (France)',
                           'mr': 'Mauritania',
                           'ms': 'Montserrat (UK)',
                           'mt': 'Malta',
                           'mu': 'Mauritius',
                           'mv': 'Maldives',
                           'mw': 'Malawi',
                           'mx': 'Mexico',
                           'my': 'Malaysia',
                           'mz': 'Mozambique',
                           'na': 'Namibia',
                           'nc': 'New Caledonia (France)',
                           'ne': 'Niger',
                           'nf': 'Norfolk Island (Australia)',
                           'ng': 'Nigeria',
                           'ni': 'Nicaragua',
                           'nl': 'Netherlands',
                           'no': 'Norway',
                           'np': 'Nepal',
                           'nr': 'Nauru',
                           'nu': 'Niue (New Zealand)',
                           'nz': 'New Zealand',
                           'om': 'Oman',
                           'pa': 'Panama',
                           'pe': 'Peru',
                           'pf': 'French Polynesia (France)',
                           'pg': 'Papua New Guinea',
                           'ph': 'Philippines',
                           'pk': 'Pakistan',
                           'pl': 'Poland',
                           'pm': 'Saint Pierre and Miquelon (France)',
                           'pn': 'Pitcairn Islands (UK)',
                           'pr': 'Puerto Rico (USA)',
                           'ps': 'Palestine',
                           'pt': 'Portugal',
                           'pw': 'Palau',
                           'py': 'Paraguay',
                           'qa': 'Qatar',
                           're': 'Reunion (France)',
                           'ro': 'Romania',
                           'rs': 'Serbia',
                           'ru': 'Russia',
                           'rw': 'Rwanda',
                           'sa': 'Saudi Arabia',
                           'sb': 'Solomon Islands',
                           'sc': 'Seychelles',
                           'sd': 'Sudan',
                           'se': 'Sweden',
                           'sg': 'Singapore',
                           'sh': 'Saint Helena (UK)',
                           'si': 'Slovenia',
                           'sj': 'Svalbard and Jan Mayen (Norway)',
                           'sk': 'Slovakia',
                           'sl': 'Sierra Leone',
                           'sm': 'San Marino',
                           'sn': 'Senegal',
                           'so': 'Somalia',
                           'sr': 'Suriname',
                           'st': 'Sao Tome and Principe',
                           'su': 'Soviet Union (former)top-level domain is still in use',
                           'sv': 'El Salvador',
                           'sx': 'Sint Maarten (Netherlands)',
                           'sy': 'Syria',
                           'sz': 'Eswatini (formerly Swaziland)',
                           'tc': 'Turks and Caicos Islands (UK)',
                           'td': 'Chad',
                           'tf': 'French Southern Territories (France)',
                           'tg': 'Togo',
                           'th': 'Thailand',
                           'tj': 'Tajikistan',
                           'tk': 'Tokelau (New Zealand)',
                           'tl': 'Timor-Leste',
                           'tm': 'Turkmenistan',
                           'tn': 'Tunisia',
                           'to': 'Tonga',
                           'tr': 'Turkey',
                           'tt': 'Trinidad and Tobago',
                           'tv': 'Tuvalu',
                           'tw': 'Taiwan',
                           'tz': 'Tanzania',
                           'ua': 'Ukraine',
                           'ug': 'Uganda',
                           'uk': 'United Kingdom',
                           'us': 'United States of America',
                           'uy': 'Uruguay',
                           'uz': 'Uzbekistan',
                           'va': 'Vatican City (Holy See)',
                           'vc': 'Saint Vincent and the Grenadines',
                           've': 'Venezuela',
                           'vg': 'British Virgin Islands (UK)',
                           'vi': 'US Virgin Islands (USA)',
                           'vn': 'Vietnam',
                           'vu': 'Vanuatu',
                           'wf': 'Wallis and Futuna (France)',
                           'ws': 'Samoa',
                           'ye': 'Yemen',
                           'yt': 'Mayotte (France)',
                           'za': 'South Africa',
                           'zm': 'Zambia',
                           'zw': 'Zimbabwe'}
    except Exception as e:
        gv.logger.error(e)
    return country_domains