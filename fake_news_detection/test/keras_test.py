'''
Created on 23 mag 2019

@author: daniele
'''
import warnings

from typing import List

import numpy

from keras_preprocessing.sequence import pad_sequences

from keras_preprocessing.text import Tokenizer

from pandas import DataFrame, read_csv

from scipy.sparse import hstack

from sklearn import random_projection

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score 

from sklearn.model_selection import train_test_split


from fake_news_detection.dao.TrainingDAO import DAOTrainingPD
from fake_news_detection.config.AppConfig import dataset_beta, resources_path
from keras.engine.sequential import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers.embeddings import Embedding
from keras.layers.pooling import GlobalMaxPool1D
from keras.layers.recurrent import LSTM
from keras.wrappers.scikit_learn import KerasClassifier
from keras import backend as K
from fake_news_detection.model.predictor import Preprocessing
import pandas
K.tensorflow_backend._get_available_gpus()
import os
#os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class FSdataframeDAO:

    def __init__(self, dir_path:str="/home/andrea/pycharm_workspace/reale-mutua_resources/dataframes/"):

        self.dir_path = dir_path



    def load(self, id:str) -> DataFrame:

        df = read_csv(self.dir_path+"/"+id+".tsv", sep='\t', encoding='utf-8')

        return df



    def store(self, df:DataFrame, id:str):

        df.to_csv(self.dir_path+"/"+id+".tsv", sep='\t', encoding='utf-8', index=False)





def get_performance(y_test:List, y_pred:List):

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(y_test, y_pred, average='weighted', labels=model1.classes_)

    recall = recall_score(y_test, y_pred, average='weighted', labels=model1.classes_)

    f1 = f1_score(y_test, y_pred, average='weighted', labels=model1.classes_)

    print("\n Evaluation performance:")

    print("\t - Accuracy:", accuracy)

    print("\t - Precision:", precision)

    print("\t - Recall:", recall)

    print("\t - F-measure:", f1, "\n")





def create_model1():

    """

    Densely (fully) connected Neural Network with 3 layers and light dropout

    (Dropout consists in randomly setting a fraction 'rate' of input units to 0

    at each update during training time, which helps prevent overfitting)

    """

    model = Sequential()

    model.add(Dense(240, input_dim=input_dim, activation='relu'))

    model.add(Dropout(rate=0.20))

    model.add(Dense(60, activation='relu'))

    model.add(Dropout(rate=0.20))

    model.add(Dense(2, activation='softmax'))   #'sigmoid'

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.summary()

    return model





def create_model2():

    """

    Turns positive integers (indexes) into dense vectors of fixed size,

    apply max pooling (sub-sample the input shape by replacing a very small input sub-array with the maximum value of this sub-array)

    and pass them to two dense layers

    """

    embedding_dim = 100

    model = Sequential()

    model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_dim))

    model.add(GlobalMaxPool1D())

    model.add(Dense(18, activation='relu'))

    model.add(Dense(3, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.summary()

    return model





def create_model3():

    """

    Turns positive integers (indexes) into dense vectors of fixed size,

    use Convolution Layer, Long Short-Term Memory layer and dense Layer

    """

    embedding_dim = 30

    model = Sequential()

    model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_dim))

    #model.add(Conv1D(filters=48, kernel_size=3, padding='same', activation='relu'))

    model.add(LSTM(18, dropout=0.2, recurrent_dropout=0.2))

    model.add(Dense(2, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.summary()

    return model





if __name__ == "__main__":



    warnings.filterwarnings("ignore")



    input_dim = -1

    vocab_size = -1



    ########## Load and split dataset ##########

    #===========================================================================
    # oo = DAOTrainingPD(dataset_beta)
    # X=oo.get_train_dataset()
    # X=X.sample(frac=1)
    # X = X.head(1000)
    # X=Preprocessing(language='en').execution(X)
    # X.to_csv(dataset_beta+"/train.csv")
    # X=pandas.read_csv(dataset_beta+"/train.csv").iloc[:, 1:]
    #===========================================================================
     #print(X.shape )
    #===========================================================================
    # X=pandas.read_csv("/home/daniele/Scaricati"+"/data.csv")
    # X=X.rename(index=str, columns={"Label": "label", "Body": "text","Headline":"title"})
    # print(X)
    # X=X.dropna()
    # ######
    # training_set= pandas.read_csv(dataset_beta +"/fake_or_real_news.csv") # dataset
    # df_app=training_set[['title','text','label']]
    # df_app['label'] = df_app['label'].map({'FAKE': 0, 'REAL':1})
    # print(df_app)
    # X=X.append(df_app)
    # print("shape after 'fake_or_real_news.csv' -->", X.shape)
    # ####    
    # print(X.groupby(['label']).agg(['count']))
    # print(X.shape )
    # X=Preprocessing().execution(X)
    # X.drop(['URLs'], axis=1)
    #===========================================================================
    X=pandas.read_csv( resources_path+"/default_train_en.csv" ).iloc[:, 1:]
    #===========================================================================
    # y= X['Label']
    # X = X.drop(['Label'], axis=1)
    # X = X.drop(['Body'], axis=1)
    # X = X.drop(['Headline'], axis=1)
    #===========================================================================
    y= X['label']
    X = X.drop(['label'], axis=1)
    X = X.drop(['text'], axis=1)
    X = X.drop(['title'], axis=1)
   
    print(X.shape )
    print(y)

    #print(df.shape)

    #df['text'] = df['oggetto'].map(str) + " " + df["body_parts"].map(str) + " " + df['attachments'].map(str)

#===============================================================================
#     X =df.drop(['label'], axis=1)
# 
#     y = df["label"]
#===============================================================================

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

    use_dense_vectors = True

    epochs = 1000

    batch_size = int(8507/20)+1





    ########## Transform data ##########



    # tf-idf vectorizer  + random projection

#===============================================================================
#     if use_dense_vectors == True:
# 
#         vect = TfidfVectorizer(min_df=10, ngram_range=(1, 1), lowercase=True)
# 
#         #vect = CountVectorizer(min_df=10, ngram_range=(1, 1), lowercase=True)
# 
#         rp = random_projection.GaussianRandomProjection(eps=0.1)                  #.SparseRandomProjection(eps=0.1)
# 
#         X_train_transf = rp.fit_transform((vect.fit_transform(X_train["text"])))
# 
#         X_test_transf = rp.transform(vect.transform(X_test["text"]))
# 
#         vocab_size = len(vect.vocabulary_)
# 
#         input_dim = X_train_transf.shape[1]                                     # Number of features (columns)
# 
# 
# 
#     # Turns words into indexes and pads this dense vectors with zeros
# 
#     else:
# 
#         tokenizer = Tokenizer()
# 
#         tokenizer.fit_on_texts(X_train["text"])
# 
#         X_train_transf_tmp = tokenizer.texts_to_sequences(X_train["text"])
# 
#         X_test_transf_tmp = tokenizer.texts_to_sequences(X_test["text"])
# 
#         arr = [len(x) for x in X_train_transf_tmp]
# 
#         print("max:", numpy.max(arr))
# 
#         print("min:", numpy.min(arr))
# 
#         print("mean:", numpy.mean(arr))
# 
#         print("median:", numpy.median(arr))
# 
#         print("std:", numpy.std(arr))
# 
#         X_train_transf = pad_sequences(X_train_transf_tmp, padding='post', maxlen=2000)
# 
#         X_test_transf = pad_sequences(X_test_transf_tmp, padding='post', maxlen=2000)
# 
#         vocab_size = len(tokenizer.word_index) + 1
# 
#         input_dim = X_train_transf.shape[1]             #Number of features (columns)
#===============================================================================
    input_dim = X.shape[1]



    ########## Training ##########

    #print("\n\t > Shape of 'X_train_transf':", X_train_transf.shape)

    print(" \t > vocabulary size:", X_train.columns)

    print(" \t > input dimension:", input_dim, "\n")

    model1 = KerasClassifier(build_fn=create_model1, epochs=epochs, batch_size=batch_size, verbose=1)
    print("fit",X_train)
#    model1.fit(X_train , y_train)

    model1.fit(X_test, y_test)
    model1.fit(X_train , y_train)


 #==============================================================================
 # Evaluation performance:
 #     - Accuracy: 0.8728813559322034
 #     - Precision: 0.8804968988798165
 #     - Recall: 0.8728813559322034
 #     - F-measure: 0.872415929124469 
 #==============================================================================

    ########## Prediction ##########

    y_pred = model1.predict(X_test )

    probs = model1.predict_proba(X_test)

    print("\n Probabilities: \n", probs[0:10])





    ########## evaluation ##########

    get_performance(y_test=y_test, y_pred=y_pred)