'''
Created on 31 mag 2019

@author: daniele
'''
from fake_news_detection.config.AppConfig import resources_path
from fake_news_detection.model.predictor import Preprocessing
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD

def create_train_file(name='default_train',path=resources_path,preprocessing=Preprocessing(),dao_dati=DAOTrainingPD(),language='en'):
    X = dao_dati.get_train_dataset()
    X=preprocessing.execution(X)
    X.drop(['URLs'], axis=1)
    X.to_csv(path+"/"+name+"_"+language+".csv")
    
    
if __name__ == '__main__':
    create_train_file()