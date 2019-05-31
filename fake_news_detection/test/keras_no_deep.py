'''
Created on 28 mag 2019

@author: daniele
'''
import warnings
from typing import List
import numpy as np
import pandas
from lightgbm import LGBMClassifier
from pandas import DataFrame, read_csv
from sklearn import random_projection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding, GlobalAveragePooling1D, GlobalMaxPool1D, LSTM, Conv1D, MaxPooling1D
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, PowerTransformer, RobustScaler
import matplotlib.pyplot as plt
from fake_news_detection.config.AppConfig import dataset_beta, picklepath,\
    resources_path
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.model.predictor import LGBMFakePredictor, Preprocessing


class FSdataframeDAO:
    def __init__(self, dir_path:str= dataset_beta):
        self.dir_path = dir_path

    def load(self, id:str) -> DataFrame:
        return read_csv(self.dir_path+"/"+id+".csv", encoding='utf-8')


def get_performance(y_test:List, y_pred:List):
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', labels=model1.classes_)
    recall = recall_score(y_test, y_pred, average='weighted', labels=model1.classes_)
    f1 = f1_score(y_test, y_pred, average='weighted', labels=model1.classes_)
    print("\n Evaluation performance:")
    print(" - y_test ->", str(list(y_test[:10])).replace("]", ""), "  . . .  ", str(list(y_test[-10:])).replace("[", ""))
    print(" - y_pred ->", str(list(y_pred[:10])).replace("]", ""), "  . . .  ", str(list(y_pred[-10:])).replace("[", ""))
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
    model.add(Dense(120, activation='relu'))
    model.add(Dropout(rate=0.20))
    model.add(Dense(60, activation='relu'))
    model.add(Dropout(rate=0.20))
    model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()
    return model



if __name__ == '__main__':    
    #===========================================================================
    # daopredictor = FSMemoryPredictorDAO(picklepath)
    # predictor=LGBMClassifier() 
    # model=LGBMFakePredictor(predictor=predictor,preprocessing=Preprocessing(), id="en_lgb")
    # model.fit()
    # daopredictor.save(model)
    #===========================================================================

    warnings.filterwarnings("ignore")

    input_dim = -1
    vocab_size = -1
    epochs = 300
    batch_size = int(23860 / 20)


    ########## Load and split dataset ##########
    df = pandas.read_csv( resources_path+"/default_train_en.csv" ).iloc[:, 1:]
    print("\n > df shape:", df.shape)
    print("\n columns", df.columns)

    # df['text_content'] = df['title'].map(str) + "\n\n\n" + df["text"].map(str)
    # X = df["text_content"]
    y = df["label"]
    df = df.drop(['title', 'text', 'label'], axis=1)
    X = df
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)



    ########## Transform data ##########

    ### tf-idf + random_projecton on only text###
    # vect = TfidfVectorizer(min_df=10, ngram_range=(1, 1), lowercase=True)
    # rp = random_projection.GaussianRandomProjection(eps=0.1)
    # X_train_transf = rp.fit_transform((vect.fit_transform(X_train)))
    # X_test_transf = rp.transform(vect.transform(X_test))

    ### numeric transformers on only numeric features ###
    num_transf = Pipeline(steps=[
                                    ('imputer', SimpleImputer(strategy='median')),
                                    ('boxcox', PowerTransformer(method='yeo-johnson', standardize=False)),
                                    ('scaler', StandardScaler(with_mean=True, with_std=True)),
                                    ('normalizer', MinMaxScaler(feature_range=(0, 1)))
                                 ])
    X_train_transf = X_train 
    X_test_transf = X_test 

    print("\n > transform complete!")
    input_dim = X_train_transf.shape[1]            # Number of features (columns)


    ########## Training ##########
    #model1 = KerasClassifier(build_fn=create_model1, epochs=epochs, batch_size=batch_size, verbose=1, validation_split=0.2)
    #model1 = LogisticRegression()
    model1 = LGBMClassifier() 
    model1.fit(X_train_transf, y_train)
    """ Plot the significance scores of feautures """
    feat_imp = pandas.Series(model1.feature_importances_, index=X.columns)
    # feat_imp = pd.Series(self.mdl.models[0].feature_importances_, index=X.columns)
    feat_imp.nlargest(50).plot(kind='barh', figsize=(8, 10))
    plt.tight_layout()
    plt.show()
    plt.close()

    ########## Prediction ##########
    # y_pred = model1.predict(X_test_transf)
    probs = model1.predict_proba(X_test_transf)
    #y_pred = ['FAKE' if single_pred[0] >= single_pred[1] else 'REAL' for single_pred in probs]
    y_pred = [0 if single_pred[0] >= single_pred[1] else 1 for single_pred in probs]
    print("\n Classes: \n", model1.classes_)
    print("\n Probabilities: \n", probs[0:10])

    ########## evaluation ##########
    get_performance(y_test=y_test, y_pred=y_pred)

