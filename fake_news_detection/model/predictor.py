'''
Created on Dec 10, 2018

@author: daniele
'''
import string
import unicodedata
import pandas as pd
from ds4biz_predictor_core.model.predictors.predictors import TransformingPredictor,\
    DS4BizPredictor
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn import metrics
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import datetime
from fake_news_detection.business.textPreprocessing import TextPreprocessor
from fake_news_detection.config.constants import QUOTES
from fake_news_detection.business.featureEngineering import preprocess_features_of_df,\
    add_new_features_to_df
from fake_news_detection.config.MLprocessConfig import new_features_mapping,\
    text_preprocessing_mapping
from fake_news_detection.model.InterfacceComunicazioni import Prestazioni
from fake_news_detection.dao.TrainingDAO import DAOTrainingElasticByDomains
from lightgbm.sklearn import LGBMClassifier
from fake_news_detection.config.AppConfig import dataset_beta, picklepath
import pandas
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO


class Preprocessing:
    def __init__(self, language:str="it"):
        self.language = language
        self.preprocess=TextPreprocessor(lang=language, mode="lemmatization", rm_stopwords=False, invalid_chars=QUOTES, encoding="utf-8")

    def _preprocessing(self, X):
        X=preprocess_features_of_df(df=X, mapping=text_preprocessing_mapping(self.preprocess))
        print('preprocessed done')
        return X
    
    def _add_features(self, X):
        X=add_new_features_to_df(df=X, mapping=new_features_mapping(self.language))
        return X    

    def execution(self,X):
        #X=self._preprocessing(X)
        return self._add_features(X)
    
    
class FakePredictor(DS4BizPredictor):
    '''
    classdocs
    '''
    def __init__(self, predictor:TransformingPredictor,
                 preprocessing:Preprocessing,id:str,task:str):
        '''
        Constructor
        '''
        now = datetime.datetime.now()
        now_string = now.strftime(('%d/%m/%Y %H:%M'))
        self.date=now_string
        self.task=task
        self.predictor_fakeness=predictor
        self.preprocessing=preprocessing
        self.id=id
        self.number_item=0
        
    def fit(self, X, y=None):
        print("dataframe",X.columns)
        X=self.preprocessing.execution(X)
        Y = X['label']
        X = X.drop(['label'], axis=1)
        print("dataframedopo",X.columns)
        self.predictor_fakeness.fit(X,Y)
        self.number_item=len(X)
        
    def predict(self, X):
        X=self.preprocessing.execution(X)
        labels_fakeness= self.predictor_fakeness.predict(X)
        return labels_fakeness
        
    def predict_proba(self,X):
        X=self.preprocessing.execution(X)
        labels_fakeness= self.predictor_fakeness.predict_proba(X)
        return labels_fakeness,X
    
    def is_partially_fittable(self):
        return True
    
    def partial_fit(self, X,y=None):
        X=self.preprocessing.execution(X)
        Y = X['label']
        X = X.drop(['label'], axis=1)
        self.predictor_fakeness.partial_fit(X,Y)
        return "OK"

        
    def get_language(self):
        return self.language
    
    def _create_prestazioni(self,predictor):
        # print(predictor.report)
        #return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, 500)
        return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, self.number_item)
        #return Prestazioni(predictor.precision,predictor.recall,predictor.accuracy,predictor.num_items)
         
    
    def get_prestazioni(self):
        return self._create_prestazioni(self.predictor_fakeness.predictor)
         
   
    def _update_prestazioni_model(self,predictor,prestazioni):
        predictor.precision = prestazioni.precision
        predictor.recall = prestazioni.recall
        predictor.accuracy = prestazioni.accuracy
        self.number_item = prestazioni.number_item
        
        
class LGBMFakePredictor(DS4BizPredictor):
    '''
    classdocs
    '''
    def __init__(self, predictor:LGBMClassifier,
                 preprocessing:Preprocessing,id:str):
        '''
        Constructor
        '''
        now = datetime.datetime.now()
        now_string = now.strftime(('%d/%m/%Y %H:%M'))
        self.date=now_string
        self.predictor_fakeness= predictor
        self.preprocessing=preprocessing
        self.id=id
        self.number_item=0
        
    def fit(self, X=None, y=None):
        X=pandas.read_csv(dataset_beta+"/train_kaggle.csv").iloc[:, 1:]
        y= X['label']
        X = X.drop(['label'], axis=1)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        X = X.drop(['URLs'], axis=1)
        self.predictor_fakeness.fit(X,y)
        
        #=======================================================================
        # print("dataframe",X.columns)
        # X=self.preprocessing.execution(X)
        # Y = X['label']
        # X = X.drop(['label'], axis=1)
        # print("dataframedopo",X.columns)
        # self.predictor_fakeness.fit(X,Y)
        # self.number_item=len(X)
        #=======================================================================
        
    def predict(self, X):
        X=self.preprocessing.execution(X)
        print(X.columns)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor_fakeness.predict(X)
        return labels_fakeness
        
    def predict_proba(self,X):
        X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor_fakeness.predict_proba(X)
        #print("labels_fakeness",labels_fakeness)
        return labels_fakeness,X
    
    def is_partially_fittable(self):
        return True
    
    def partial_fit(self, X,y=None):
        X=self.preprocessing.execution(X)
        Y = X['label']
        X = X.drop(['label'], axis=1)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        self.predictor_fakeness.partial_fit(X,Y)
        return "OK"

        
    def get_language(self):
        return self.language
    
    def _create_prestazioni(self,predictor):
        # print(predictor.report)
        #return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, 500)
        return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, self.number_item)
        #return Prestazioni(predictor.precision,predictor.recall,predictor.accuracy,predictor.num_items)
         
    
    def get_prestazioni(self):
        return self._create_prestazioni(self.predictor_fakeness.predictor)
         
   
    def _update_prestazioni_model(self,predictor,prestazioni):
        predictor.precision = prestazioni.precision
        predictor.recall = prestazioni.recall
        predictor.accuracy = prestazioni.accuracy
        self.number_item = prestazioni.number_item
        
                
    #===========================================================================
    # def update_prestazioni(self,prestazioni:OutputPrestazioni):
    #     self._update_prestazioni_model(self.predictor_sentiment.predictor,prestazioni.sentiment)
    #     self._update_prestazioni_model(self.predictor_dispatching.predictor,prestazioni.dispatching)
    #===========================================================================
#===============================================================================
#   
# def prestazioni_model(dati,predictor):
#     df = dataframe_from_social_data_no_split(dati)
#     df = df.dropna()
#     # calcolo prestazioni per il sentiment
#     y=predictor.predict(df[['commento']])
#     prestazioni_sentiment=prestazioni(df['sentiment'],y[0])
#     prestazioni_dispatching = prestazioni_multi_label(df['categorie'],y[1])
#     # print(df[['commento']])
#     # print(y[1])
#     output_prestazioni = OutputPrestazioni(prestazioni_sentiment, prestazioni_dispatching)
#     return output_prestazioni
#       
# def prestazioni(y_test,y_pred):
#     y_test=y_test.str.lower()
#     accuracy=metrics.accuracy_score(y_test,y_pred)
#     precision=metrics.precision_score(y_test,y_pred,average="macro")
#     recall=metrics.recall_score(y_test,y_pred,average="macro")
#     # print(accuracy,precision,recall)
#     return Prestazioni(precision,recall,accuracy,len(y_test))
# 
# def prestazioni_multi_label(y_test,y_pred):
#     y_test_addative=list()
#     for i in range(len(y_test)):
#         if y_pred[i] in y_test[i]:
#             y_test_addative.append(y_pred[i])
#         else:
#             y_test_addative.append(y_test[i][0])
#     y_test_addative= pd.Series(y_test_addative)
#     return prestazioni(y_test_aòddative,y_pred)
#===============================================================================

if __name__ == '__main__':    
    X=pandas.read_csv(dataset_beta+"/train_kaggle.csv").iloc[:, 1:]
    print(X.columns)
    #===========================================================================
    # daopredictor = FSMemoryPredictorDAO(picklepath)
    # predictor=LGBMClassifier() 
    # model=LGBMFakePredictor(predictor=predictor,preprocessing=Preprocessing(), id="en_lgb")
    # model.fit()
    # daopredictor.save(model)
    #===========================================================================
    '''
    list_domains = [('www.wikileaks.com', 'FAKE')]
    print(list_domains)
    dao_train = DAOTrainingElasticByDomains(list_domains)
    training_set=dao_train.get_train_dataset(limit=100000000)
     '''
    
    
#===============================================================================
#     preprocessing = Preprocessing("en")
#     training_set = pd.read_csv("/home/camila/Scrivania/csv_fandango/final_df_1503.csv", delimiter = '\t')
#     X = preprocessing.execution(training_set)
#     print(X.columns) 
# 
#     X1 = X._get_numeric_data()
#     print( X1, "without numeric ")
#     X2 = pd.concat([X1 , X['label']], axis = 1)
#     print( "adding label", X2. columns)
#     X2.to_csv("/home/camila/Scrivania/forcorrelation.csv")     
#     
#===============================================================================
    
    
    
    
    
    
    