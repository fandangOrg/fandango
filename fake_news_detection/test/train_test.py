'''
Created on 8 feb 2019

@author: daniele
'''
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains,\
    DAOTrainingPD
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO, DAONewsElastic
from fake_news_detection.apps.training_model import Train_model
from fake_news_detection.config.AppConfig import dataset_beta
from fake_news_detection.model.predictor import Preprocessing
#
#
#===============================================================================
# train_config=Train_model()
# daopredictor = FSMemoryPredictorDAO("/home/daniele/resources/fandango/")
# #training_set = train_config.load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.1)
# list_domains = DAONewsElastic().get_domain()
# print(list_domains)
# dao_train = DAOTrainingElasticByDomains(list_domains)
# training_set=dao_train.get_train_dataset()
# training_set_final = train_config.preprocess_df(training_set)
# train_config.training("test1", training_set_final, daopredictor)
#===============================================================================
#===============================================================================
# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())
#===============================================================================



oo = DAOTrainingPD(dataset_beta)
X=oo.get_train_dataset()
X = X.head(3000)
print(X.shape )
X=Preprocessing(language='en').execution(X)
Y = X['label']
X = X.drop(['label'], axis=1)
X = X.drop(['text'], axis=1)
X = X.drop(['litle'], axis=1)

print(X.shape )
print(X.columns)
