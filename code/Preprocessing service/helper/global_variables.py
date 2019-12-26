# -*- coding: utf-8 -*-
import os
from helper import helper
from helper.custom_log import init_logger

# ====================================================================================
# ------------------------- GLOBAL VARIABLES PREPROCESSING ---------------------------
# ====================================================================================

newspaper = None
thread = None
service = None
es_host = None
es_port = None
kf_host = None
kf_port = None
kafka_server = None
country_domains = None
logger = None
log_file_name = None
default_field = None
person_es_index = None
org_es_index = None
idf_es_index = None
save_article_txt = None


def init():
    """ Init method: Initialises the global variables required in the preprocessing step
    """
    global newspaper
    global thread
    global service
    global es_host
    global es_port
    global kf_host
    global kf_port
    global kafka_server
    global country_domains
    global logger
    global log_file_name
    global default_field
    global person_es_index
    global org_es_index
    global idf_es_index
    global save_article_txt

    logger = init_logger(__name__, testing_mode=False)
    thread = None
    service = None
    log_file_name = os.path.join("www", "app_logs","app.log")
    default_field = 'Unknown'
    person_es_index = "fdg-ap-person"
    org_es_index = "fdg-ap-organization"
    idf_es_index = "crawled-articles"

    es_host = "fandangoedge02"
    es_port = "9220"
    kf_host = "fandangoedge01"
    kf_port = "9092"
    # ------------------------------------
    save_article_txt = 'last_article.txt'

    kafka_server = kf_host + ":" + kf_port
    newspaper = helper.collect_publisher_from_allmediaLink()
    country_domains = {'ac':	'Ascension Island (UK)',
                        'ad':	'Andorra',
                        'ae':	'United Arab Emirates',
                        'af':	'Afghanistan',
                        'ag':	'Antigua and Barbuda',
                        'ai':	'Anguilla (UK)',
                        'al':	'Albania',
                        'am':	'Armenia',
                        'ao':	'Angola',
                        'ar':	'Argentina',
                        'as':	'American Samoa (USA)',
                        'at':	'Austria',
                        'au':	'Australia',
                        'aw':	'Aruba (Netherlands)',
                        'ax':	'Aland Islands (Finland)',
                        'az':	'Azerbaijan',
                        'ba':	'Bosnia and Herzegovina',
                        'bb':	'Barbados',
                        'bd':	'Bangladesh',
                        'be':	'Belgium',
                        'bf':	'Burkina Faso',
                        'bg':	'Bulgaria',
                        'bh':	'Bahrain',
                        'bi':	'Burundi',
                        'bj':	'Benin',
                        'bm':	'Bermuda (UK)',
                        'bn':	'Brunei',
                        'bo':	'Bolivia',
                        'br':	'Brazil',
                        'bs':	'Bahamas',
                        'bt':	'Bhutan',
                        'bv':	'Bouvet Island (Norway)',
                        'bw':	'Botswana',
                        'by':	'Belarus',
                        'bz':	'Belize',
                        'ca':	'Canada',
                        'cc':	'Cocos (Keeling) Islands (Australia)',
                        'cd':	'Democratic Republic of the Congo',
                        'cf':	'Central African Republic',
                        'cg':	'Republic of the Congo',
                        'ch':	'Switzerland',
                        'ci':	'Cote d\'Ivoire',
                        'ck':	'Cook Islands (New Zealand)',
                        'cl':	'Chile',
                        'cm':	'Cameroon',
                        'cn':	'China',
                        'co':	'Colombia',
                        'cr':	'Costa Rica',
                        'cu':	'Cuba',
                        'cv':	'Cabo Verde',
                        'cw':	'Curacao (Netherlands)',
                        'cx':	'Christmas Island (Australia)',
                        'cy':	'Cyprus',
                        'cz':	'Czechia',
                        'de':	'Germany',
                        'dj':	'Djibouti',
                        'dk':	'Denmark',
                        'dm':	'Dominica',
                        'do':	'Dominican Republic',
                        'dz':	'Algeria',
                        'ec':	'Ecuador',
                        'ee':	'Estonia',
                        'eg':	'Egypt',
                        'er':	'Eritrea',
                        'es':	'Spain',
                        'et':	'Ethiopia',
                        'eu':	'European Union',
                        'fi':	'Finland',
                        'fj':	'Fiji',
                        'fk':	'Falkland Islands (UK)',
                        'fm':	'Federated States of Micronesia',
                        'fo':	'Faroe Islands (Denmark)',
                        'fr':	'France',
                        'ga':	'Gabon',
                        'gb':	'United Kingdom',
                        'gd':	'Grenada',
                        'ge':	'Georgia',
                        'gf':	'French Guiana (France)',
                        'gg':	'Guernsey (UK)',
                        'gh':	'Ghana',
                        'gi':	'Gibraltar (UK)',
                        'gl':	'Greenland (Denmark)',
                        'gm':	'Gambia',
                        'gn':	'Guinea',
                        'gp':	'Guadeloupe (France)',
                        'gq':	'Equatorial Guinea',
                        'gr':	'Greece',
                        'gs':	'South Georgia and the South Sandwich Islands (UK)',
                        'gt':	'Guatemala',
                        'gu':	'Guam (USA)',
                        'gw':	'Guinea-Bissau',
                        'gy':	'Guyana',
                        'hk':	'Hong Kong (China)',
                        'hm':	'Heard Island and McDonald Islands (Australia)',
                        'hn':	'Honduras',
                        'hr':	'Croatia',
                        'ht':	'Haiti',
                        'hu':	'Hungary',
                        'id':	'Indonesia',
                        'ie':	'Ireland',
                        'il':	'Israel',
                        'im':	'Isle of Man (UK)',
                        'in':	'India',
                        'io':	'British Indian Ocean Territory (UK)',
                        'iq':	'Iraq',
                        'ir':	'Iran',
                        'is':	'Iceland',
                        'it':	'Italy',
                        'je':	'Jersey (UK)',
                        'jm':	'Jamaica',
                        'jo':	'Jordan',
                        'jp':	'Japan',
                        'ke':	'Kenya',
                        'kg':	'Kyrgyzstan',
                        'kh':	'Cambodia',
                        'ki':	'Kiribati',
                        'km':	'Comoros',
                        'kn':	'Saint Kitts and Nevis',
                        'kp':	'North Korea',
                        'kr':	'South Koreav',
                        'kw':	'Kuwait',
                        'ky':	'Cayman Islands (UK)',
                        'kz':	'Kazakhstan',
                        'la':	'Laos',
                        'lb':	'Lebanon',
                        'lc':	'Saint Lucia',
                        'li':	'Liechtenstein',
                        'lk':	'Sri Lanka',
                        'lr':	'Liberia',
                        'ls':	'Lesotho',
                        'lt':	'Lithuania',
                        'lu':	'Luxembourg',
                        'lv':	'Latvia',
                        'ly':	'Libya',
                        'ma':	'Morocco',
                        'mc':	'Monaco',
                        'md':	'Moldova',
                        'me':	'Montenegro',
                        'mg':	'Madagascar',
                        'mh':	'Marshall Islands',
                        'mk':	'North Macedonia (formerly Macedonia)',
                        'ml':	'Mali',
                        'mm':	'Myanmar (formerly Burma)',
                        'mn':	'Mongolia',
                        'mo':	'Macau (China)',
                        'mp':	'Northern Mariana Islands (USA)',
                        'mq':	'Martinique (France)',
                        'mr':	'Mauritania',
                        'ms':	'Montserrat (UK)',
                        'mt':	'Malta',
                        'mu':	'Mauritius',
                        'mv':	'Maldives',
                        'mw':	'Malawi',
                        'mx':	'Mexico',
                        'my':	'Malaysia',
                        'mz':	'Mozambique',
                        'na':	'Namibia',
                        'nc':	'New Caledonia (France)',
                        'ne':	'Niger',
                        'nf':	'Norfolk Island (Australia)',
                        'ng':	'Nigeria',
                        'ni':	'Nicaragua',
                        'nl':	'Netherlands',
                        'no':	'Norway',
                        'np':	'Nepal',
                        'nr':	'Nauru',
                        'nu':	'Niue (New Zealand)',
                        'nz':	'New Zealand',
                        'om':	'Oman',
                        'pa':	'Panama',
                        'pe':	'Peru',
                        'pf':	'French Polynesia (France)',
                        'pg':	'Papua New Guinea',
                        'ph':	'Philippines',
                        'pk':	'Pakistan',
                        'pl':	'Poland',
                        'pm':	'Saint Pierre and Miquelon (France)',
                        'pn':	'Pitcairn Islands (UK)',
                        'pr':	'Puerto Rico (USA)',
                        'ps':	'Palestine',
                        'pt':	'Portugal',
                        'pw':	'Palau',
                        'py':	'Paraguay',
                        'qa':	'Qatar',
                        're':	'Reunion (France)',
                        'ro':	'Romania',
                        'rs':	'Serbia',
                        'ru':	'Russia',
                        'rw':	'Rwanda',
                        'sa':	'Saudi Arabia',
                        'sb':	'Solomon Islands',
                        'sc':	'Seychelles',
                        'sd':	'Sudan',
                        'se':	'Sweden',
                        'sg':	'Singapore',
                        'sh':	'Saint Helena (UK)',
                        'si':	'Slovenia',
                        'sj':	'Svalbard and Jan Mayen (Norway)',
                        'sk':	'Slovakia',
                        'sl':	'Sierra Leone',
                        'sm':	'San Marino',
                        'sn':	'Senegal',
                        'so':	'Somalia',
                        'sr':	'Suriname',
                        'st':	'Sao Tome and Principe',
                        'su':	'Soviet Union (former)top-level domain is still in use',
                        'sv':	'El Salvador',
                        'sx':	'Sint Maarten (Netherlands)',
                        'sy':	'Syria',
                        'sz':	'Eswatini (formerly Swaziland)',
                        'tc':	'Turks and Caicos Islands (UK)',
                        'td':	'Chad',
                        'tf':	'French Southern Territories (France)',
                        'tg':	'Togo',
                        'th':	'Thailand',
                        'tj':	'Tajikistan',
                        'tk':	'Tokelau (New Zealand)',
                        'tl':	'Timor-Leste',
                        'tm':	'Turkmenistan',
                        'tn':	'Tunisia',
                        'to':	'Tonga',
                        'tr':	'Turkey',
                        'tt':	'Trinidad and Tobago',
                        'tv':	'Tuvalu',
                        'tw':	'Taiwan',
                        'tz':	'Tanzania',
                        'ua':	'Ukraine',
                        'ug':	'Uganda',
                        'uk':	'United Kingdom',
                        'us':	'United States of America',
                        'uy':	'Uruguay',
                        'uz':	'Uzbekistan',
                        'va':	'Vatican City (Holy See)',
                        'vc':	'Saint Vincent and the Grenadines',
                        've':	'Venezuela',
                        'vg':	'British Virgin Islands (UK)',
                        'vi':	'US Virgin Islands (USA)',
                        'vn':	'Vietnam',
                        'vu':	'Vanuatu',
                        'wf':	'Wallis and Futuna (France)',
                        'ws':	'Samoa',
                        'ye':	'Yemen',
                        'yt':	'Mayotte (France)',
                        'za':	'South Africa',
                        'zm':	'Zambia',
                        'zw':	'Zimbabwe'}