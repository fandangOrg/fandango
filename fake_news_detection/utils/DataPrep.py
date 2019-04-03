'''
Created on 17 ott 2018

@author: camila
'''
import pandas as pd
import re 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import numpy as np 
from fake_news_detection.config.AppConfig import dataset_beta
from dask.dataframe.io.csv import read_csv


class DataPrep(object):
    '''
    Temporary this function upload dataset
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.df = pd.read_csv(dataset_beta) # dataset
    
    
    def printInfodb(self):
        
        print("######DATA SET DIMENSION:#######",self.df.shape)
        print("######Let's take a look of the dataset:#######", self.df.head())
        print("######dataset balanced:#######",self.df.groupby('label').size())
        lens = self.df.text.str.len()
        #=======================================================================
        # plt.hist(lens)
        # plt.show()
        # 
        #=======================================================================
        
    def preprocessingdb(self):
        
        df_p = self.df.set_index('Unnamed: 0') #set the index
        df_p['text'] = df_p['text'].map(lambda com : self.clean_text(com))
        print("######dataset preprocessed######")
        return(df_p)
     
    def clean_text(self,text):
        
        text = text.lower()
        text = re.sub(r"what's", "what is ", text)
        text = re.sub(r"\'s", " ", text)
        text = re.sub(r"\'ve", " have ", text)
        text = re.sub(r"can't", "can not ", text)
        text = re.sub(r"n't", " not ", text)
        text = re.sub(r"i'm", "i am ", text)
        text = re.sub(r"\'re", " are ", text)
        text = re.sub(r"\'d", " would ", text)
        text = re.sub(r"\'ll", " will ", text)
        text = re.sub(r"\'scuse", " excuse ", text)
        text = re.sub('\W', ' ', text)
        text = re.sub('\s+', ' ', text)
        text = text.strip(' ')
        return text        
        
    
    def splitdataset(self,df_p):
        """
        split a train and a test
        """
        
        y = self.df.label
        df1 = self.df.drop("label", axis = 1)
        X_train, X_test, y_train, y_test = train_test_split(df1['text'], y, test_size=0.33, random_state=1234)
        print("###### DATASET SPLITTED ######")
        return(X_train, X_test, y_train, y_test)
    
    
    def vectorizetfidf(self,X_train, X_test, y_train, y_test):
        """
        vectorize samples to pass them to the model script
        """
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
        tfidf_train = tfidf_vectorizer.fit_transform(X_train)
        tfidf_test = tfidf_vectorizer.transform(X_test)
        
        
        tfidf_df_train = pd.DataFrame(tfidf_train.A, columns=tfidf_vectorizer.get_feature_names())#convert in dataset
        tfidf_df_test = pd.DataFrame(tfidf_test.A, columns=tfidf_vectorizer.get_feature_names())
        
        tfidf_df_train= tfidf_df_train[tfidf_df_train.columns[1850:-100]] #remove some noise 
        tfidf_df_test = tfidf_df_test[tfidf_df_test.columns[1850:-100]]
        
        print("###### VECTORIZE DONE! ######")
        return(tfidf_df_train,tfidf_df_test, y_train, y_test)
        
        
def clean_text(text):
    
    text = text.lower()
    text = text.replace("\n"," ")
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "can not ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r"\'scuse", " excuse ", text)
    text = re.sub('\W', ' ', text)
    text = re.sub(r'[0-9]*', ' ', text)

    text = re.sub('\s+', ' ', text)
    text = text.strip(' ')
    return text        



if __name__  == "__main__":
    #print(clean_text("casa mia oggi 34 "))
    
    p = read_csv("/home/camila/workspace/fandango-fake-news/fake_news_detection/resources/guardian.csv",sep='|')
    p.columns
    #===========================================================================
    # d = DataPrep() 
    # d.printInfodb()
    # d.preprocessingdb()
    # X_train, X_test, y_train, y_test = d.splitdataset()
    # #print(X_train.head())
    # del d
    # 
    #===========================================================================
    
    