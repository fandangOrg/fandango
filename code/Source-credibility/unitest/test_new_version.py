from connectors.source_credibility_connector import SourceCredibilityConnector
from connectors.elasticsearch_connector import ElasticsearchConnector
from unitest.input_examples.input_preprocessed_examples import data_preprocessed
from fandango_models.article import Article
import time

# =========cona=====================================================================
elasticsearch_connector = ElasticsearchConnector(host="localhost", port="9220")
elasticsearch_connector.connect()

# 1. Create input document
art_obj = data_preprocessed.get("data")

art_doc: Article = Article()
document: Article = art_doc.article_from_dict(data=art_obj)

# 2. Create object
source_credibility_connector = SourceCredibilityConnector(
    elasticsearch_connector=elasticsearch_connector)

# 3. Apply analysis
start_time = time.time()
print(f"init: {start_time}")
res = source_credibility_connector.apply_analysis(
    document=document)
end_time = time.time()
print(f"end: {end_time}")
print(f"Duration: {end_time-start_time}")
