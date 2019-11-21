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
from fake_news_detection.config.AppConfig import dataset_beta  ,\
    resources_path_train
import pandas
from sklearn.ensemble.voting_classifier import VotingClassifier
from sklearn.preprocessing.label import LabelEncoder
from sklearn.model_selection._split import train_test_split
from sklearn.metrics.classification import accuracy_score, precision_score,\
    recall_score, f1_score
from pytorch_pretrained_bert.modeling import BertForPreTraining
from pytorch_pretrained_bert.tokenization import BertTokenizer
import torch
from torch.utils.data.dataset import TensorDataset
from torch.utils.data.sampler import RandomSampler
from torch.utils.data.dataloader import DataLoader
import bert
import pandas as pd 


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
    
    
class BertPreprocessing(Preprocessing):
    def __init__(self,MAX_SEQ_LENGTH=40):
        self.tokenizer= BertTokenizer.from_pretrained('bert-base-multilingual-uncased', do_lower_case=True)
        self.MAX_SEQ_LENGTH=MAX_SEQ_LENGTH
        
        
    def _transform(self,df,data_colum,label=None ):
        print("transof")
        if label:
            df = df.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = x[data_colum], 
                                                                   text_b = None, 
                                                                   label = x[label]), axis = 1)
        else:
            s=df[data_colum][0]
            df = df.apply(lambda x: bert.run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a = s, 
                                                                   text_b = None,
                                                                   label = 'a'))
        return df
    
    def execution(self,df,data_colum,label_colum=None):
        df=self._transform(df,data_colum,label_colum)
        if label_colum:
            features = bert.run_classifier.convert_examples_to_features(df, list(set(df[label_colum])), self.MAX_SEQ_LENGTH,  self.tokenizer)
        else:
            features = bert.run_classifier.convert_examples_to_features(df,list('a'), self.MAX_SEQ_LENGTH,  self.tokenizer)
        return features
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
        y_pred = [self.predictor.classes_[0] if single_pred[0] >= single_pred[1] else self.predictor.classes_[1] for single_pred in probs]
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
        
        
class BERTFakePredictor(DS4BizPredictor):
    '''
    classdocs
    '''
    def __init__(self, predictor:BertForPreTraining,
                 preprocessing:BertPreprocessing,id:str):
        '''
            Constructor
        '''
        now = datetime.datetime.now()
        now_string = now.strftime(('%d/%m/%Y %H:%M'))
        self.date=now_string
        self.predictor= predictor
        self.predictor.id=id
        self.predictor.to('cpu')
        self.preprocessing=preprocessing
        
        
    def fit(self, X=None, y=None):
        raise NotImplemented()
    
    def predict(self, X):
        raise NotImplemented()
        
        
    def _input_converter(self,features,train=False):
        if train:
            all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
            all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
            all_label_ids = torch.tensor([f.label_id for f in features], dtype=torch.long)
        else:
            all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
            all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
            all_label_ids = None
            
        return all_input_ids,all_input_mask,all_label_ids
    
    def predict_proba(self,X):
        features=self.preprocessing.execution(X,'text')
        l=list()
        for f in features:
            l.append(f.input_ids)
            break
        self.predictor.eval()
        all_input_ids = torch.tensor(l, dtype=torch.long)
        all_input_ids.to('cpu')
    
        labels_fakeness=self.predictor(all_input_ids)
        result=labels_fakeness.data[0]
        fake=float(result[0])
        real=float(result[1])
        old_min=min([fake,real])-1
        old_range = max([fake,real])+1 - old_min
        new_min = 0
        new_range =1 - new_min
        output = [ (n - old_min) / old_range * new_range + new_min  for n in [fake,real]]
        return [output], pd.DataFrame(['UNDEFINED'],columns=['Features'])
    
    def is_partially_fittable(self):
        return True
    
    def partial_fit(self, X,y=None):
        raise NotImplemented()

        
    def get_language(self):
        raise NotImplemented()
    
    def _create_prestazioni(self,predictor):
       raise NotImplemented()
         
    
    def get_prestazioni(self):
       raise NotImplemented()
         
   
    def _update_prestazioni_model(self,predictor,prestazioni):
        raise NotImplemented()
        
        
        
        
def get_performance(y_test, y_pred,classes):
    print("-->",y_test)
    print("-->",y_pred)
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
    for lang,train in [('it','default_train_v2_en.csv')]:
        X=pandas.read_csv(resources_path_train+"/"+train ).iloc[:, 1:] 
        print(X.columns)
        preprocessing = Preprocessing("en")
        X = preprocessing.execution(X)
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
    
    
    
    
    
    
    
