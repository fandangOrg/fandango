'''
Created on 8 feb 2019

@author: daniele
'''
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO, DAONewsElastic
from fake_news_detection.apps.training_model import Train_model
#
#
train_config=Train_model()
daopredictor = FSMemoryPredictorDAO("/home/daniele/resources/fandango/")
#training_set = train_config.load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.1)
list_domains = DAONewsElastic().get_domain()
print(list_domains)
dao_train = DAOTrainingElasticByDomains(list_domains)
training_set=dao_train.get_train_dataset()
training_set_final = train_config.preprocess_df(training_set)
train_config.training("test1", training_set_final, daopredictor)
