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
import pandas
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



#===============================================================================
# oo = DAOTrainingPD(dataset_beta)
# X=oo.get_train_dataset()
# #X = X.head(3000)
# print(X.shape )
# X=Preprocessing(language='en').execution(X)
# X.to_csv(dataset_beta+"/train.csv")
# Y = X['label']
# X = X.drop(['label'], axis=1)
# X = X.drop(['text'], axis=1)
# X = X.drop(['litle'], axis=1)
# 
# print(X.shape )
# print(X.columns)
#===============================================================================
#X=pandas.read_csv(dataset_beta+"/train.csv").iloc[:, 1:]

class Train_model:
    
    
    def load_df(self,path_to_dataset:str, sample_size:float=0.05) -> DataFrame:
        df = read_csv(path_to_dataset, sep = '|')
        print("\n > load dataframe from \'", path_to_dataset, "\'" )
        if sample_size < 1.0:
            sample = df.sample(frac=sample_size)
            print("\n > sample (", sample_size, "%)", "[", sample.columns, "]")
            return sample
        else:
            return df
    
    
    def preprocess_df(self,training_set:DataFrame, path_for_store_preprocessed_df:str="./prova.csv", store:bool=True) -> DataFrame:
        training_set_modified = preprocess_features_of_df(df=training_set.dropna(), mapping=text_preprocessing_mapping)
        print("\n 1) Training_set_modified: \n", training_set_modified.iloc[0, :])
        training_set_improved = add_new_features_to_df(df=training_set_modified.dropna(), mapping=new_features_mapping)
        print("\n 2) Training_set_improved: \n", training_set_improved.iloc[0, :])
        training_set_final = training_set_improved.dropna()
        print("\n 3) Training_set_final: \n", training_set_final.iloc[0, :])
        if store:
            training_set_final.to_csv(path_for_store_preprocessed_df)
        return training_set_final
    
    
    def training(self,model_name:str, training_set_final, daopredictor):
        y = training_set_final['label']
        X = training_set_final.drop(['label'], axis=1)
        print("Shape of X:", X.shape)
        print("Columns of X:", X.columns)
        request_transformer = ColumnTransformer(transforming_mapping)
        name_classifier = 'RandomForestClassifier'
        params_classifier = {"n_estimators" : 10 , 'criterion' : 'gini'}
        request_model = CreationRequest(name_classifier, params_classifier)
        model = TransformingPredictorFactory().create(request_model, request_transformer)
        model.id = model_name
        model.fit(X, y)
        daopredictor.save(model)
        print("\n Training of '" + model_name + "': DONE")
        print("   - Accuracy:", model.predictor.accuracy)
        print("   - Precision:", model.predictor.precision)
        print("   - Recall:", model.predictor.recall)
        print("   - F-measure:",  2 * (model.predictor.precision * model.predictor.recall) / (model.predictor.precision + model.predictor.recall))
    
    
    def evaluate(self,model_name:str, test_set_final, daopredictor):
        y_test = test_set_final['label']
        X_test = test_set_final.drop(['label'], axis=1)
        model = daopredictor.get_by_id(model_name)
        y_pred = model.predict(X_test)
        print("\n Evaluation of \'" + model_name + "\' on " + str(len(y_test)) + " observations:")
        print("   - Accuracy:", accuracy_score(y_test, y_pred))
        print("   - Precision:", precision_score(y_test, y_pred, average='macro'))
        print("   - Recall:", recall_score(y_test, y_pred, average='macro'))
        print("   - F-measure:",  f1_score(y_test, y_pred, average='macro'))



X=pandas.read_csv("/home/daniele/Scaricati"+"/data.csv")
print(X)
print(X.groupby(['Label']).agg(['count']))
print(X.shape )
y= X['Label']
X = X.drop(['Label'], axis=1)
X = X.drop(['Body'], axis=1)
X = X.drop(['Headline'], axis=1)
X=X.mean()
print(X)
