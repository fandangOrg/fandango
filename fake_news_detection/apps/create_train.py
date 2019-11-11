'''
Created on 31 mag 2019

@author: daniele
'''
from fake_news_detection.config.AppConfig import resources_path, path_training
from fake_news_detection.model.predictor import Preprocessing
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD,\
    DAOTrainingPDDomain

def create_train_file(name='default_train',path=resources_path,preprocessing=Preprocessing('en'),dao_dati=DAOTrainingPD(),language='en'):
    X = dao_dati.get_train_dataset()
    print(path+"/"+name+"_text_"+language+".csv")
    X=preprocessing.execution(X)
    X.to_csv(path+"/"+name+"_text_"+language+".csv")
#    X.to_csv(path+"/"+name+"_"+language+".csv")
    
    
if __name__ == '__main__':
    #create_train_file(name='default_train_v3_only_kaggle_new_features')
    for file_train,lang in [('dataset_dutch.csv','nl'),("dataset_italian.csv","it"),("dataset_spanish.csv","es")]:
        print(lang,file_train)
        create_train_file(name='default_train_domains',path=resources_path,
                          preprocessing=Preprocessing(lang),
                          dao_dati=DAOTrainingPDDomain(path_training+"/"+file_train, "|"),
                          language=lang)
        