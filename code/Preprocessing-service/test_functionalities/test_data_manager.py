from helper.data_manager import DataManager

# Test Kill Elasticsearch
dm = DataManager(service="new_test")
dm.init_elasticsearch_manager()

# Test Kill Kafka
from services.services import PreprocessingServices
serv: PreprocessingServices = PreprocessingServices()

serv.offline_service()