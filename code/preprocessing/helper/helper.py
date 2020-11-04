from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import numpy as np
from datetime import datetime
import time
import os
import pytz
import json
import pycountry
import whois
import tld
import hashlib
import tldextract
import pandas as pd
from helper import global_variables as gv
from flair.models import SequenceTagger
from restcountries import RestCountryApiV2 as rapi
from urllib.parse import urlparse
from PIL import Image
import requests
from io import BytesIO


def get_stop_words():
    stopwords = ['Contacta Al Autor', 'Subscribe To ', 'Ediciones'
                 'about', 'help', 'privacy', 'legal', 'feedback', 'sitemap',
                 'profile', 'account', 'mobile', 'sitemap', 'facebook', 'myspace',
                 'twitter', 'linkedin', 'bebo', 'friendster', 'stumbleupon',
                 'youtube', 'vimeo', 'store', 'mail', 'preferences', 'maps',
                 'password', 'imgur', 'flickr', 'search', 'subscription', 'itunes',
                 'siteindex', 'events', 'stop', 'jobs', 'careers', 'newsletter',
                 'subscribe', 'academy', 'shopping', 'purchase', 'site-map',
                 'shop', 'donate', 'newsletter', 'product', 'advert', 'info',
                 'tickets', 'coupons', 'forum', 'board', 'archive', 'browse',
                 'howto', 'how to', 'faq', 'terms', 'charts', 'services',
                 'contact', 'plus', 'admin', 'login', 'signup', 'register',
                 'developer', 'proxy', 'images']
    return stopwords


def parser_wikipedia(wiki_url):
    req = requests.get(wiki_url)
    b = BeautifulSoup(req.content, 'lxml')
    return b


def parser_newspapers(links, i):
    data = links[i]
    newspapers = []
    if i == 15:
        split_data = data.split('\n')[2:-5]
        newspapers += split_data
    else:
        split_data = data.split('\n\n')
        npaper = [split_data[ide].split('\n') for ide, j in enumerate(split_data)]
        if npaper is not None and npaper:
            for k, el in enumerate(npaper):
                if i == 17:
                    garbage_until = 4
                else:
                    garbage_until = 0

                if k > garbage_until and len(el) > 1:
                    if el[0] == '' and el[1] != '':
                        newspapers.append(el[1])
    return newspapers


def get_fake_media():
    fake_media = ['Bullion Bulls Canada', 'The Fourth Revolutionary War', 'Count Down To Zero Time',
                  'Knowledge of Today', 'Canada Free Press', 'Now The End Begins',
                  'Prepper Website', 'American Free Press', 'Neon Nettle',
                  'MilNews.ca', 'Rense', 'Political Blind Spot', 'Irrussianality',
                  'Zaytunarjuwani Blog', 'Assassination Science', 'Dutchsinse',
                  'Eco Watch', 'Educate-yourself', 'Empire Sports', 'Expose 1933',
                  'Free Wood Post', 'Grean Ville Post', 'Guardian LV', 'Health Nut News',
                  'Heart Land', 'Heatst', 'Guzlers', 'Investment Watch Blog',
                  'Judicial Watch', 'katohika', 'Land Over Baptist',
                  'Love This Pic', 'Mint Press News', 'MRC', 'National Review',
                  'National Review', 'Naural Blaze', 'Nutritional Anarchy',
                  'Observer', 'Pak Alert Press', 'Patrioit Post', 'Pravda',
                  'Project Veritas', 'Real Farmacy', 'Responsible Technology',
                  'Responsible Tecnology', 'Sovereign Man', 'The Beaverton',
                  'The fifth Column News', 'The Liberty Mill', 'The Mideast Beast',
                  'The Valley Report', 'Wiki Leaks', 'The Liberty Mill',
                  'Wolf Street', 'News Volos', 'Paron', 'Tilest WRA',
                  'Zero Hedge', 'ROMA FA SCHIFO', 'AboveTopSecret','Star',
                  'Ksipnistere']
    return fake_media


def get_list_newspapers():
    WIKI_URL_es = "https://en.wikipedia.org/wiki/List_of_newspapers_in_Spain"
    WIKI_URL_it = "https://en.wikipedia.org/wiki/List_of_newspapers_in_Italy"
    WIKI_URL_du = "https://en.wikipedia.org/wiki/List_of_newspapers_in_Belgium"

    b = []
    b.append(parser_wikipedia(wiki_url=WIKI_URL_es))
    b.append(parser_wikipedia(wiki_url=WIKI_URL_it))
    b.append(parser_wikipedia(wiki_url=WIKI_URL_du))

    links = [i.text for b_el in b for i in b_el.find_all(name='tbody')]

    # Get Newspapers
    idx = [3, 4, 15, 17]

    temp_np = [parser_newspapers(links, i) for i in idx]
    # Flatten list
    newspapers_final = [y for x in temp_np for y in x]

    return newspapers_final


def domain_stop_words():
    domain_stop_words = ['.be', '.com', '.es', '.eu', '.fr', '.gr',
                         '.hu', '.it', '.uk', '.org', '.net',
                         '.int', '.edu', '.gov', '.mil', '.arp',
                         'www.', 'https://']
    return domain_stop_words


def remove_domain_words(source_domain, domain_stop_words):
    for stopWord in domain_stop_words:
        source_domain = source_domain.replace(stopWord, '')
    return source_domain


def get_country_by_code(country_code):
    try:
        country_domain = gv.country_domains
        country = country_domain[country_code]
    except Exception as e:
        gv.logger.warning(e)
        country = "Not Specified"
    return country


def extract_org_info(source_domain):
    source_domain_data = None
    required_fields = {"domain_name", "creation_date", "expiration_date", "status", "name", "org",
                       "city", "state", "zipcode", "country"}
    try:
        # WhoisIP
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

            # 4) String keys
            standard_keys = ["status", "name", "org", "city", "state", "zipcode"]
            for i in standard_keys:
                if i not in source_domain_data.keys():
                    source_domain_data[i] = gv.org_default_field
                else:
                    source_domain_data[i] = str(source_domain_data[i])

            # 5) Country
            if 'country' in source_domain_data.keys() and w['country'] is not None:
                country_code = source_domain_data['country']
                country_data = pycountry.countries.get(alpha_2=country_code)
                if country_data is None:
                    country_code = source_domain.split('.')[-1]
                    try:
                        source_domain_data['country'] = gv.country_domains[country_code.lower()]
                    except Exception as e:
                        source_domain_data['country'] = gv.default_field
                else:
                    source_domain_data['country'] = str(country_data.name)

        # Check
        ttd = tldextract.extract(source_domain)
        if source_domain_data["domain_name"] is None:
            # tldExtractor
            source_domain_data["domain_name"] = ttd.registered_domain

        # Add a new key for whois name
        source_domain_data["whois_name"] = source_domain_data["name"]
        if source_domain_data["name"] is gv.org_default_field:
            source_domain_data["name"] = ttd.domain

    except Exception as e:
        gv.logger.error(e)
    return source_domain_data


def check_organization_data(organization, organizations_list, threshold=90):
    final_org = 'Unknown'
    parent_org = 'Not Specified'
    similarity = []
    org_data = {'name': '', 'country': '', 'parent_org': 'Not Specified'}
    try:
        domain = tld.get_fld(url=organization)
    except Exception as e:
        domain = tldextract.extract(organization)
        domain = domain.domain
    sub_domain = None

    #--------------------------------
    if domain is None:
        domain = organization
    # --------------------------------

    # Check sub-domain
    if len(domain.split('.'))>2:
        organization = domain.split('.')[0]
        sub_domain = '.'.join(domain.split('.')[1:])

    try:
        if sub_domain is not None:
            w = dict(whois.whois(url=sub_domain))
        else:
            # Make the query
            w = dict(whois.whois(url=organization))

        # Check if there is a list
        if 'domain_name' in list(w.keys()) and isinstance(w['domain_name'], list) and w['domain_name'] is not None:
            domain = w['domain_name'][1]
        elif 'domain_name' in list(w.keys()) and not isinstance(w['domain_name'], list) and w['domain_name'] is not None:
            domain = w['domain_name']

        # 1) Get the Country
        if 'country' in list(w.keys()) and w['country'] is not None:
            country_code = w['country']
            country_data = pycountry.countries.get(alpha_2=country_code)
            if country_data is None:
                country_code = organization.split('.')[-1]
                try:
                    country = gv.country_domains[country_code]
                except Exception as e:
                    country = 'Not Specified'
            else:
                country = str(country_data.name)

        else:
            if sub_domain is None:

                country_code = organization.split('.')[-1]
            else:
                country_code = domain.split('.')[-1]
            country = get_country_by_code(country_code)

        # 2) Get the Name
        if 'name' in list(w.keys()) and w['name'] is not None:
            # Compute distance between domain and name
            distance = fuzz.ratio(w['name'].replace(' ', '').lower(), domain.lower())
            # Get the name of the organization
            if distance >= threshold:
                final_org = w['name']
                parent_org = 'Not Specified'
                done = False
            # Require a new procedure to obtain the name
            else:
                if 'org' in list(w.keys()):
                    parent_org = w['org']
                else:
                    parent_org = w['name']
                done = True
        else:
            done = True
    except Exception as e:
        country = 'Not Specified'
        parent_org = 'Not Specified'
        final_org = 'Unknown'
        w = {'domain_name': None}
        done = True
    
    if done:
        # If there is no sub-domain
        if (sub_domain is None or w['domain_name'] is None ) and "blogspot" not in domain:
            organization = domain.split('.')[0]
        elif "blogspot" in domain:
            organization = organization.split('.')[0]
        # Get the name of the organization using Similarity

        try:
            org_lower = [org.replace(' ', '').lower() for org in organizations_list]
            # Compute similarity
            for i, org in enumerate(org_lower):
                similarity.append(fuzz.ratio(org, organization.lower()))

            if np.max(similarity) > threshold:
                idx = np.argmax(np.array(similarity))
                final_org = organizations_list[idx]
            else:
                final_org = organization.title()

        except Exception as e:
            gv.logger.warning(e)

    org_data['name'] = final_org.title()
    org_data['country'] = country
    if parent_org is None:
        parent_org = 'Not Specified'

    org_data['parent_org'] = parent_org
    return org_data



def check_authorname_org(authorName, organizations_list, threshold=90):
    try:
        similarity = []
        is_org = False

        org_lower = [org.replace(' ', '').lower() for org in organizations_list]

        # Compute similarity
        for i, org in enumerate(org_lower):
            similarity.append(fuzz.ratio(org, authorName.replace(' ', '').lower()))

        if np.max(similarity) >= threshold:
            idx = np.argmax(np.array(similarity))
            final_org = organizations_list[idx]
            is_org = True

    except Exception as e:
        gv.logger.error(e)
        is_org = False

    return is_org


def collect_publisher_from_allmediaLink():
    fileDir = 'resources'
    fileName = 'newspapers.json'
    key = 'Newspapers'
    media_links = ['https://spain.allmedialink.com/newspaper/',
                   'https://spain.allmedialink.com/online-newsportal/',
                   'https://italy.allmedialink.com/',
                   'https://italy.allmedialink.com/online-newsportal/',
                   'https://belgium.allmedialink.com/',
                   'https://belgium.allmedialink.com/online-newsportal/',
                   'https://france.allmedialink.com/',
                   'https://france.allmedialink.com/online-newsportal/',
                   'https://greece.allmedialink.com/',
                   'https://greece.allmedialink.com/online-newsportal/',
                   'https://uk.allmedialink.com/',
                   'https://uk.allmedialink.com/online-newsportal/',
                   'https://usa.allmedialink.com/']

    total_np = []
    total_time = 86400
    done = False
    newspaper_resource = os.path.join(fileDir, fileName)
    if os.path.isfile(newspaper_resource):
        # if exists check the date
        prev_date = os.path.getmtime(newspaper_resource)
        current_date = time.time()
        if int(current_date - prev_date) >= total_time:
            done = True
    else:
        # if there is no file (first time)
        done = True
    if done:
        for link in media_links:
            try:
                # Extract Newspapers from links
                response = requests.get(link, timeout=10)
                content = str(response.content)
                soup = BeautifulSoup(content, 'lxml')
                # Extract all tags
                tags = soup.findAll("div", {"class": "logo-caption"})
                # Get Newspapers
                newspapers = [tag.find('a').contents[0] for tag in tags]
                # Remove duplicates
                final_newspapers = list(set(newspapers))
                # Append
                total_np += final_newspapers
            except Exception as e:
                msg = str(e) + ' The last updated document will be used in this case.'
                gv.logger.warning(msg)
                # Use the last updated
                if os.path.exists(newspaper_resource):
                    with open(newspaper_resource) as json_file:
                        total_np = json.load(json_file)
                        # Get the list
                        total_np = total_np[key]
                # Get out of the for loop
                break

        # FANDANGO LIST
        fandango_list = ['Europa Today', 'Il Fatto Quotidiano', "Ansa"
                         'Milano Finanza', 'AttivoNews', 'ilsapereepotere2', 'El Mundo Today',
                         'Errado de Aragon', 'Meneame', 'Hay Noticia', 'HLN', 'Het Nieuwsblad',
                         'Newsmonkey', 'GVA', 'HBVL', 'La Verdad', 'El Norte de Castilla',
                         'El Diario Montañés', 'El Norte de Castilla', 'Diario Vasco',
                         'Levante-EMV', 'Heraldo', 'Faro de Vigo', 'La Nueva España',
                         'El Correo', 'El Periodico', 'La Voz de Galicia', 'Cope', 'Agencia EFE',
                         'Europa Press', 'El Salto Diario', 'La Marea', 'El Plural', 'El Independiente',
                         'Voz Populi', 'Periodista Digital', 'Libertad Digital', 'Huffington Post',
                         'Mediterráneo Digital']

        total_np += fandango_list
        total_np = list(set(total_np))
        # Save the file
        data = {key: total_np}
        with open(newspaper_resource, 'w') as outfile:
            json.dump(data, outfile)
    else:
        # Read JSON and put it the list
        with open(newspaper_resource) as json_file:
            data = json.load(json_file)
        total_np = data[key]

    return total_np

def get_datetime():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S %z")
    return date_time

def extract_country_from_code(country_code):
    country = None
    try:
        country_data = pycountry.countries.get(alpha_2=country_code.upper())
        if country_data is not None:
            country = str(country_data.official_name)
        else:
            country = gv.country_domains[country_code.lower()]
    except Exception as e:
        pass
    return country

def extract_publisher_info(source_domain, list_of_websites=None, threshold=95):
    source_domain_data = None
    required_fields = {"domain_name", "creation_date", "expiration_date", "status", "name", "org",
                       "city", "state", "zipcode", "country", "suffix", "whois_name", "whois_country",
                       "nationality"}
    try:
        # WhoisIP
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

            # 4) Updated date
            if "updated_date" not in source_domain_data.keys():
                source_domain_data["updated_date"] = gv.org_default_field
            else:
                if isinstance(source_domain_data["updated_date"], list):
                    source_domain_data["updated_date"] = source_domain_data["creation_date"][0]
                # Add time zone utc
                if isinstance(source_domain_data["updated_date"], datetime):
                    d = pytz.UTC.localize(source_domain_data["updated_date"])
                    source_domain_data["updated_date"] = d.strftime("%Y-%m-%d %H:%M:%S %Z")

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
            ttd = tldextract.extract(source_domain)
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
                country_data = extract_country_from_code(country_code)
                source_domain_data['whois_country'] = str(country_data)
            else:
                source_domain_data['whois_country'] = gv.org_default_field

            # Analyse country via suffix
            country_code = source_domain.split('.')[-1]
            country_data = extract_country_from_code(country_code)
            if country_data is None:
                if source_domain_data["whois_country"] != gv.org_default_field:
                    source_domain_data['country'] = source_domain_data["whois_country"]
                else:
                    source_domain_data['country'] = gv.org_default_field
            else:
                source_domain_data['country'] = str(country_data)
        try:
            source_domain_data["nationality"] = rapi.get_countries_by_name(source_domain_data["country"])[0].demonym
        except Exception as e:
            source_domain_data["nationality"] = gv.org_default_field

        # Only keep the required keys
        source_domain_data = dict((key,value) for key, value in source_domain_data.items() if key in list(required_fields))
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


def remove_duplicate_strings_from_list(str_lst: list, min_char=3, fuzzy=False, fuzzy_threshold=80):
    unique_str_lst: list = str_lst
    try:
        if len(str_lst) > 0:
            # Constraints
            str_lst: list = [i for i in str_lst if i is not None and
                             len(i) >= min_char and len(i.split(" ")) > 1]
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


def fuzzy_similarity_search(data: list, threshold: float = 80):
    new_data = []
    try:
        for i, element in enumerate(data):
            if not new_data:
                new_data.append(element)

            for j, new_element in enumerate(data):
                dist = fuzz.ratio(element, new_element)

                # They are not equals
                if dist < threshold:
                    if new_element not in new_data:
                        res_dist = [fuzz.ratio(new_element, existing_element) for existing_element in new_data]
                        if all(x < threshold for x in res_dist):
                            new_data.append(new_element)
    except Exception as e:
        pass
        # gv.logger.error(e)
    return new_data


def create_websites_db(filepath, countries):
    df = pd.DataFrame()
    try:
        for cont in countries:
            gv.logger.info("Extracting data from ", cont)
            df_temp = pd.read_excel(filepath, sheet_name=cont, skip_blank_lines=False)
            cols = list(df_temp.columns)
            moDf = df_temp.dropna(how='any', subset=cols[1:4])

            # Replace nans by unknown
            moDf = moDf.fillna("N/A")
            df = pd.concat([df, moDf], axis=0)
    except Exception as e:
        gv.logger.error(e)
    return df


def create_csv_from_df(df, filepath):
    try:
        df.to_csv(filepath)
    except Exception as e:
        gv.logger.error(e)


def generate_uuid_article(url):
    identifier = ""
    try:
        identifier = (hashlib.sha256(".".join(urlparse(url).netloc.split(".")[-2:]).encode('utf-8')).hexdigest() +
                      hashlib.sha256(urlparse(url).path.encode('utf-8')).hexdigest())
    except Exception as e:
        gv.logger.error(e)
    return identifier


def generate_uuid_from_string(data_uuid):
    identifier = ""
    try:
        if len(data_uuid) == 1:
            hash_fuct = hashlib.sha512
            n_iter = 1
        else:
            hash_fuct = hashlib.sha256
            n_iter = 2
        for i in range(n_iter):
            identifier += hash_fuct(data_uuid[i].encode('utf-8')).hexdigest()
    except Exception as e:
        gv.logger.error(e)
    return identifier


def extract_domain_from_url(url):
    domain = None
    try:
        info = tldextract.extract(url)
        domain = info.registered_domain
    except Exception as e:
        gv.logger.error(e)
    return domain

def retrieve_image_by_url(url):
    img = None
    try:
        response = requests.get(url, timeout=1)
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        gv.logger.error(e)
    return img

def filter_by_size(img):
    filter = False
    try:
        filter_size = 100*100
        image_size = img.size[0]*img.size[1]
        # if the image is smaller than the filter size
        if image_size <= filter_size:
            filter = True
    except Exception as e:
        gv.logger.error(e)
    return filter

def filter_by_aspect_ratio(img):
    filter = False
    try:

        filter_ratio_h = 5
        filter_ratio_w = 0.5
        image_ratio = img.width / img.height

        # Horizontal banner
        if image_ratio >= filter_ratio_h:
            filter = True
            gv.logger.warning("Horizontal banner")

        # Vertical banner
        if image_ratio <= filter_ratio_w:
            filter = True
            gv.logger.warning("Vertical banner")
    except Exception as e:
        gv.logger.error(e)
    return filter


def download_ner_models():
    supported_languages: dict = {"en": "ner-fast", "fr": "fr-ner",
                                 "de": "de-ner", "nl": "nl-ner-rnn",
                                 "xx": "ner-multi-fast"}
    for lang, model_name in supported_languages.items():
        gv.logger.info(f"Downloading model for language {lang}")
        tagger = SequenceTagger.load(model_name)
