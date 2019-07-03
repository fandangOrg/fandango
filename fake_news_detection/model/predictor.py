'''
Created on Dec 10, 2018

@author: daniele
'''
from ds4biz_predictor_core.model.predictors.predictors import TransformingPredictor,\
    DS4BizPredictor
import datetime
from fake_news_detection.business.textPreprocessing import TextPreprocessor
from fake_news_detection.config.constants import QUOTES
from fake_news_detection.business.featureEngineering import preprocess_features_of_df,\
    add_new_features_to_df
from fake_news_detection.config.MLprocessConfig import new_features_mapping,\
    text_preprocessing_mapping, config_factory
from fake_news_detection.model.InterfacceComunicazioni import Prestazioni
from lightgbm.sklearn import LGBMClassifier
from fake_news_detection.config.AppConfig import dataset_beta  
import pandas
from sklearn.ensemble.voting_classifier import VotingClassifier
from sklearn.preprocessing.label import LabelEncoder
from sklearn.model_selection._split import train_test_split
from sklearn.metrics.classification import accuracy_score, precision_score,\
    recall_score, f1_score


class Preprocessing:
    def __init__(self, language:str="it"):
        self.language = language
        #self.preprocess=TextPreprocessor(lang=language, mode="lemmatization", rm_stopwords=False, invalid_chars=QUOTES, encoding="utf-8")

    #===========================================================================
    # def _preprocessing(self, X):
    #     X=preprocess_features_of_df(df=X, mapping=text_preprocessing_mapping(self.preprocess))
    #     print('preprocessed done')
    #     return X
    #===========================================================================
    
    def _add_features(self, X):
        X=add_new_features_to_df(df=X, mapping=new_features_mapping(self.language))
        return X    

    def execution(self,X):
        #X=self._preprocessing(X)
        return self._add_features(X)
    
'''
MODELLO CHE USA SOLO FEATURES NUMERICHE, E TOGLIE LE FEATURES COME TEXT E TITLE.
'''    
class FakePredictor(DS4BizPredictor):
    '''
    classdocs
    '''
    def __init__(self, predictor:TransformingPredictor,
                 preprocessing:Preprocessing,id:str):
        '''
        Constructor
        '''
        now = datetime.datetime.now()
        now_string = now.strftime(('%d/%m/%Y %H:%M'))
        self.date=now_string
        self.predictor=predictor
        #print("predictor",self.predictor)
        self.preprocessing=preprocessing
        self.id=id
        self.number_item=0
        
    def fit(self, X, y=None,preprocessing=False):
        if preprocessing:
            X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        Y = X['label']
        X = X.drop(['label'], axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X,Y , test_size=0.2)
        self.predictor.fit(X_train,y_train)
        probs = self.predictor.predict_proba(X_test)
        y_pred = [0 if single_pred[0] >= single_pred[1] else 1 for single_pred in probs]
        get_performance(y_test=y_test, y_pred=y_pred,classes=self.predictor.classes_)        
        self.number_item=len(X_train)
        self.predictor.fit(X ,Y)
        
    def predict(self, X):
        X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor.predict(X)
        return labels_fakeness
        
    def predict_proba(self,X):
        X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor.predict_proba(X)
        return labels_fakeness,X
    
    def is_partially_fittable(self):
        return True
    
    def partial_fit(self, X,y=None):
        X=self.preprocessing.execution(X)
        Y = X['label']
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        X = X.drop(['label'], axis=1)
        self.predictor.partial_fit(X,Y)
        return "OK"

        
    def get_language(self):
        return self.language
    
    def _create_prestazioni(self,predictor):
        # print(predictor.report)
        #return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, 500)
        return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, self.number_item)
        #return Prestazioni(predictor.precision,predictor.recall,predictor.accuracy,predictor.num_items)
         
    
    def get_prestazioni(self):
        return self._create_prestazioni(self.predictor.predictor)
         
   
    def _update_prestazioni_model(self,predictor,prestazioni):
        predictor.precision = prestazioni.precision
        predictor.recall = prestazioni.recall
        predictor.accuracy = prestazioni.accuracy
        self.number_item = prestazioni.number_item
        
class KerasFakePredictor(FakePredictor):
    
    def partial_fit(self, X,y=None):
        X=self.preprocessing.execution(X)
        Y = X['label']
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        X = X.drop(['label'], axis=1)
        self.predictor.fit(X,Y)
        return "OK"
    
    
class VotingClassifierPredictor(FakePredictor):
    def __init__(self,preprocessing:Preprocessing,id):
        lista_modelli=[]
        self.preprocessing=preprocessing
        for k in range(1,5):
            estimator= config_factory.create_model_by_configuration("fandango", str(k))
            #print("analsisi",k,estimator)
            lista_modelli.append((str(k),FakePredictor(estimator,preprocessing,id)))
        #print("lista_modelli",lista_modelli)
        self.eclf = VotingClassifier(estimators=lista_modelli, voting='soft',n_jobs=-1 )
        self.id=id
    
    def partial_fit(self, X,y=None): 
        X['label']= self.le_.transform(X['label'])
        for clf in self.eclf.estimators_:
            clf.partial_fit(X[['title']],X['label'])
            
    def fit(self,X,preprocessing=False):
        if preprocessing:
            X=self.preprocessing.execution(X)
        
        self.le_ = LabelEncoder().fit(X['label'])
        Y = X['label']
        
        self.eclf.fit(X,Y) 
        print("FITTED")
        objs=[self.eclf,self.le_]
        for clf in self.eclf.estimators_:
            print(clf.predictor.predictor.accuracy)
            
        print(self.eclf.accuracy)

            
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
        self.predictor= predictor
        self.preprocessing=preprocessing
        self.id=id
        self.number_item=0
        self.language=preprocessing.language
        
    def fit(self, X=None, y=None):
        y= X['label']
        X = X.drop(['label'], axis=1)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        
        #=======================================================================
        # print("dataframe",X.columns)
        # X=self.preprocessing.execution(X)
        # Y = X['label']
        # X = X.drop(['label'], axis=1)
        # print("dataframedopo",X.columns)
        # self.predictor.fit(X,Y)
        # self.number_item=len(X)
        #=======================================================================
        
    def predict(self, X):
        X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor.predict(X)
        return labels_fakeness
        
    def predict_proba(self,X):
        X=self.preprocessing.execution(X)
        X = X.drop(['text'], axis=1)
        X = X.drop(['title'], axis=1)
        labels_fakeness= self.predictor.predict_proba(X)
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
        self.predictor.partial_fit(X,Y)
        return "OK"

        
    def get_language(self):
        return self.language
    
    def _create_prestazioni(self,predictor):
        # print(predictor.report)
        #return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, 500)
        return Prestazioni(predictor.precision, predictor.recall, predictor.accuracy, self.number_item)
        #return Prestazioni(predictor.precision,predictor.recall,predictor.accuracy,predictor.num_items)
         
    
    def get_prestazioni(self):
        return self._create_prestazioni(self.predictor.predictor)
         
   
    def _update_prestazioni_model(self,predictor,prestazioni):
        predictor.precision = prestazioni.precision
        predictor.recall = prestazioni.recall
        predictor.accuracy = prestazioni.accuracy
        self.number_item = prestazioni.number_item_lgb
        
def get_performance(y_test, y_pred,classes):
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', labels= classes)
    recall = recall_score(y_test, y_pred, average='weighted', labels= classes)
    f1 = f1_score(y_test, y_pred, average='weighted', labels= classes)
    print("\n Evaluation performance:")
    print(" - y_test ->", str(list(y_test[:10])).replace("]", ""), "  . . .  ", str(list(y_test[-10:])).replace("[", ""))
    print(" - y_pred ->", str(list(y_pred[:10])).replace("]", ""), "  . . .  ", str(list(y_pred[-10:])).replace("[", ""))
    print("\t - Accuracy:", accuracy)
    print("\t - Precision:", precision)
    print("\t - Recall:", recall)
    print("\t - F-measure:", f1, "\n")
    
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
    
    
    
    
    
    
    
