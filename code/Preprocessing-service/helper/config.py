import os
from helper.custom_log import init_logger

log_file_name = os.path.join("app_logs", "app.log")
logger = init_logger(__name__, testing_mode=False)
thread = None
service = None

# Pre-processing Params
default_field = 'Unknown'
org_default_field = 'N/A'
person_es_index = "fdg-ap-person"
org_es_index = "fdg-ap-organization"
idf_es_index = "crawled-articles"
ner_library = "spacy"

# Ports and Hosts
# Add environment variables
host = os.getenv("HOST_PORT") if "HOST_PORT" in os.environ else "0.0.0.0"
port = int(os.getenv("API_PORT")) if "API_PORT" in os.environ else 5001


""" Elasticsearch environment variables"""
if os.getenv('ELASTICSEARCH_SERVER') is not None:
    es_host = str(os.getenv('ELASTICSEARCH_SERVER'))
else:
    es_host = "fandangoedge02"

if os.getenv('ELASTICSEARCH_PORT') is not None:
    es_port = str(os.getenv('ELASTICSEARCH_PORT'))
else:
    es_port = "9220"

if os.getenv('ELASTICSEARCH_INDEX_ANNOT') is not None:
    temp_es_index = str(os.getenv('ELASTICSEARCH_INDEX_ANNOT'))
else:
    temp_es_index = "article_preprocessed_temp"

""" Kafka environment variables"""
if os.getenv('KAFKA_SERVER') is not None:
    kf_host = str(os.getenv('KAFKA_SERVER'))
else:
    kf_host = "fandangoedge01"

if os.getenv('KAFKA_PORT') is not None:
    kf_port = str(os.getenv('KAFKA_PORT'))
else:
    kf_port = "9092"

if os.getenv('KAFKA_TOPIC_CONSUMER') is not None:
    topic_consumer = str(os.getenv('KAFKA_TOPIC_CONSUMER'))
else:
    topic_consumer = 'input_raw'

if os.getenv('KAFKA_TOPIC_PRODUCER') is not None:
    topic_producer = str(os.getenv('KAFKA_TOPIC_PRODUCER'))
else:
    topic_producer = 'input_preprocessed'

kafka_server = kf_host + ":" + kf_port
group_id = 'upm_group'

# Process name
offline_service_name = "Offline service"
online_service_name = "Online service"
manual_annotation_service_name = "Manual Annotation service"
experimental_service_name = "Experimental Offline service"

service_name = "Pre-processing"
error_msg = "An error occurred when applying pre-processing"
running_msg = "Running"
aborted_msg = "Aborted"
stop_msg = "Stopped"
already_stop_msg = "The service is already stopped"
countries_websites = ["spain", "italy", "greece", "belgium", "uk", "usa"]
resources_dir = "resources"
csv_filepath = "domains.csv"

# Country Information
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