from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import requests
import elasticsearch
import numpy as np
from datetime import datetime
import time
import os
import json
import pycountry
import whois
import tld
import tldextract
from helper import global_variables as gv


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
        gv.logger.warning(e)
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


def tail(f, n, offset=None):
    """Reads a n lines from f with an offset of offset lines.  The return
    value is a tuple in the form ``(lines, has_more)`` where `has_more` is
    an indicator that is `True` if there are more lines in the file.
    """
    avg_line_length = 74
    to_read = n + (offset or 0)

    while 1:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None]
        avg_line_length *= 1.3


def kafka_running(group="David", server="fandangoedge01:9092", consumer_timeout_ms=3000):
    import kafka
    try:
        client =kafka.KafkaClient(server)
        if len(client.topic_partitions) > 0:
            client.close()
            return True
        else:
            return False
    except Exception as e:
        return False

def elastic_running(host="host", port="port"):
    try:
        elastic = elasticsearch.Elasticsearch([{'host': host, 'port': port}],max_retries=2,
                                              http_compress=True)
        if elastic.ping(request_timeout=1):
            elastic.transport.close()
            return True
        else:
            return False
    except Exception as e:
        return False

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
        fandango_list = ['Europa Today', 'Il Fatto Quotidiano',
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

def save_last_article(id):
    try:
        with open(gv.save_article_txt, 'w+') as f:
            text = f.read()
            text = str(id)
            f.seek(0)
            f.write(text)
            f.truncate()
    except Exception as e:
        gv.logger.error(e)