'''
Created on Oct 24, 2018

@author: daniele
'''
import pandas as pd

def get_train_dataset():
    from fake_news_detection.config.AppConfig import dataset_beta
    training_set= pd.read_csv(dataset_beta+"/"+"fake.csv") # dataset
    #print(training_set.dropna(subset = ['title'])['title'])
    df=training_set.dropna(subset = ['title','text'])
    
    df=df[['title','text']]
    df['label']='FAKE'
    training_set= pd.read_csv(dataset_beta+"/"+"guardian.csv",sep='\t') # dataset
    training_set['label']='REAL'
    df=df.append(training_set)
    training_set= pd.read_csv(dataset_beta+"/fake_or_real_news.csv") # dataset
    df_app=training_set[['title','text','label']]
    df=df.append(df_app)
    #df=df_app
    df=df.dropna(subset = ['title','text','label'])
    #df['text']=df['text'].swifter.apply(clean_text)
    #df['title'].swifter.apply(clean_text)
    print(df.groupby(['label']).agg(['count']))
    return df

if __name__ == '__main__':
    get_train_dataset()