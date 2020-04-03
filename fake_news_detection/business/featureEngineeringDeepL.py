'''
Created on 31 mar 2020

@author: daniele
'''
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing.label import LabelEncoder
import bert
from bert import run_classifier
from pytorch_pretrained_bert.tokenization import BertTokenizer
from fake_news_detection.config.constants import MAX_SEQ_LENGTH
from keras.preprocessing.sequence import pad_sequences
from bert.run_classifier import InputFeatures
import pickle
from fake_news_detection.config.AppConfig import path_features_deep_learning,\
    resources_path
import torch
from pygments.unistring import No
import pandas
LABEL_COLUMN = 'label'
DATA_COLUMN = 'text'


class FeaturesEngineering:
    
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-uncased', do_lower_case=True)

    
    def load_dati(self,name):
            # saving
        try:
            with open(path_features_deep_learning+name+".pickle", 'rb') as handle:
                return pickle.load(handle)
        except:
            return None
               
    def save_dati(self,name,obj):
        # saving
        with open(path_features_deep_learning+name+".pickle", 'wb') as handle:
            pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


    def _converter_feature(self,data_InputExamples,name_save):
        features = []
        for (ex_index, example) in enumerate(data_InputExamples):
            if ex_index % 100 == 0:
                print("Writing example %d of %d" % (ex_index, len(data_InputExamples)))
            tokens_a = self.tokenizer.tokenize(example.text_a)
            token = self.tokenizer.convert_tokens_to_ids(tokens_a)
         
            input_ids = pad_sequences([token], maxlen=MAX_SEQ_LENGTH, dtype="long", 
                                      value=0, truncating="post", padding="post")[0]
            
             
            input_mask = [0] * len(input_ids)
            features.append(
                    InputFeatures(input_ids=input_ids,
                                  input_mask=input_mask,
                                  segment_ids=input_mask,
                                  label_id = example.label))
            
        if name_save:
            self.save_dati(name_save,features)
    #features = bert.extract_features.convert_examples_to_features(data_InputExamples, MAX_SEQ_LENGTH, tokenizer)
        return features


        # Convert our train and test features to InputFeatures that BERT understands.
        #features = bert.run_classifier.convert_examples_to_features(data_InputExamples, label_list, MAX_SEQ_LENGTH, self.tokenizer)
        #return features
    
    def _transform_input(self,data_df,Y):
        if Y:
            train_InputExamples = data_df.apply(lambda x: run_classifier.InputExample(guid=None, # Globally unique ID for bookkeeping, unused in this example
                                                                       text_a = x[DATA_COLUMN], 
                                                                       text_b = None, 
                                                                       label = x[LABEL_COLUMN]), axis = 1)
        
        else:
            s = data_df['text'][0]
            train_InputExamples = data_df.apply(lambda x: bert.run_classifier.InputExample(guid=None,  # Globally unique ID for bookkeeping, unused in this example
                                                                   text_a=s,
                                                                   text_b=None,
                                                                   label='a'))
        
        return train_InputExamples  




    '''
        df_text : corpo della news
        df_style: features stylografiche
        Y= label fake/nofake
        output:
        lista composta nel seguente ordine da:
        tensor_text,tensor_text_style,tensor_mask, label(opzionale)
    '''
    def transform_in_tensor(self,df_text,df_features_style=None,Y=False,name_save=None):
        features_text = None
        if name_save!= None:
            print('provo a caricare',name_save)
            features_text=self.load_dati(name_save)
            
        if features_text==None:
            train_InputExamples =  self._transform_input(df_text,Y)
            features_text = self._converter_feature(train_InputExamples,name_save)
            
        all_tensors=list()
        #=======================================================================
        # all_tensors['tensor_text']=torch.tensor([f.input_ids for f in features_text], dtype=torch.long)
        # all_tensors['tensor_mask']=torch.tensor([f.input_mask for f in features_text], dtype=torch.long)
        # all_tensors['tensor_text_style']=torch.tensor(df_features_style.values, dtype=torch.float)
        # if Y:
        #     all_tensors['tensor_label']=torch.tensor([f.label_id for f in features_text], dtype=torch.long)
        #=======================================================================
        
        all_tensors.append(torch.tensor([f.input_ids for f in features_text], dtype=torch.long))
        all_tensors.append(torch.tensor(df_features_style.values, dtype=torch.float))
        all_tensors.append(torch.tensor([f.input_mask for f in features_text], dtype=torch.long))
        if Y:
            all_tensors.append(torch.tensor([f.label_id for f in features_text], dtype=torch.long))
        
        
        return all_tensors
    
# Load all files from a directory in a DataFrame.
def load_directory_data():
    le = LabelEncoder()
    file_train="/home/daniele/resources/fandango/train_preprocessed/default_train_v3_only_kaggle_new_features_text_en.csv"
    file_test=None
    #file_train="/home/daniele/resources/fandango/train_preprocessed/default_train_domains_text_en.csv"
    #file_test="/home/daniele/resources/fandango/train_preprocessed/default_train_v3_only_kaggle_new_features_text_en.csv"
    #'/home/daniele/Scaricati/train.csv'
    train_df = pd.read_csv(file_train)
    #'/home/daniele/Scaricati/test.csv'
    if file_test is not None:
        test_df = pd.read_csv(file_test)
    else:
        train_df,  test_df =  train_test_split(train_df , test_size=0.2)

    #===========================================================================
    # a=train_df
    # train_df=test_df
    # test_df=a
    #===========================================================================
    
    train_df=train_df.dropna()
    test_df=test_df.dropna()
    #train_df = train_df.sample(500)
    #test_df = test_df.sample(200)

    print("TRAIN SIZE=",len(train_df)) 
    print("TEST SIZE=",len(test_df))
    #===========================================================================
    # train_df[DATA_COLUMN] = train_df[[DATA_COLUMN]].apply(lambda col: sentences_build(col))
    # 
    # test_df[DATA_COLUMN] = test_df[[DATA_COLUMN]].apply(lambda col: sentences_build(col))
    #     
    #===========================================================================
    train_df[LABEL_COLUMN] = train_df[[LABEL_COLUMN]].apply(lambda col: le.fit_transform(col))
    test_df[LABEL_COLUMN] = test_df[[LABEL_COLUMN]].apply(lambda col: le.transform(col))
    print(len(set(train_df[LABEL_COLUMN])))
    #return train_df[[DATA_COLUMN,LABEL_COLUMN]], test_df[[DATA_COLUMN,LABEL_COLUMN]]
    return train_df, test_df

    
if __name__ == '__main__':
    train, test=load_directory_data()
    
    for lang,train in [('en','default_train_v3_only_kaggle_new_features_text_en.csv')]:
        print("leggi train")
        X = pandas.read_csv(resources_path + "/" + train).iloc[:, 1:]
        X=X.sample(100)
        X['label'] = X['label'].map({0: "FAKE", 1: "GOOD"})
        X['label'] = X['label'].map({"FAKE":0,"GOOD":1})
        train_text=X[[DATA_COLUMN,LABEL_COLUMN]]
        X = X.drop(['text','title'], axis=1)
        #X = X.drop(['title'], axis=1)
        features_style = X.drop(['label'], axis=1)
        
        
        train_InputExamples =  FeaturesEngineering().transform_in_tensor(train_text,features_style,Y=True)
    #for i in train_InputExamples:
    #    print(i.__dict__)
    
        