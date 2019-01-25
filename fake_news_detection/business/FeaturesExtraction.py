'''
Created on Oct 25, 2018

@author: daniele
'''
import re
from nltk.tokenize import sent_tokenize
import treetaggerwrapper
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin
import math
 
class DataFrameColumnExtracter(TransformerMixin):

    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.column]
    
class SampleExtractor(BaseEstimator, TransformerMixin):

    def __init__(self, name_columns,vect=None):
        self.name_columns = name_columns  # e.g. pass in a column name to extract
        self.vect=vect
        
    def transform(self, X, y=None):
        if self.vect:
            t=self.vect.transform(X[self.name_columns])
            print(self.name_columns)
            print(t.shape)
            return t
        else:
            t= X[[self.name_columns]]
        print(self.name_columns)
        print(t.shape)
        return np.array(t)

    def fit(self, X, y=None):
        if self.vect:
            self.vect.fit(X[self.name_columns])
        return self  # generally does nothing
    

def features_extraction(df,features,column):
    if type(features)==list:
        for f in features:
            print(f.__name__)
            df = _add_feature(df,column,f.__name__,f)
            print(df.columns) 
            
    return df
    

def features_extraction_JJ(df,column):
    df['new_f_ADJ']= list(count_ADJ(df['text']))

    
def _add_feature(df,column,name,funct):
    df["new_f_"+column+"_"+name]=df[column].apply(funct)
    return df

def count_no_alfanumber(text):
    line = re.sub(r"[a-z0-9\s]", "", text.lower())
    l=len(line)
    if l<1:
        l=1
    return math.log(l)

def len_words(text):
    return math.log(len(set(text.split(" "))))

def len_sentences(text):
    return len(sent_tokenize(text))



def tag(s,lang="en",numlines=True):
    app=list()
    print("start ... ")

    tagger = treetaggerwrapper.TreeTagger(TAGLANG=lang)
    for el in tagger.tag_text(s,numlines=numlines):
       
        yield el.split("\t")
        #if len(items)==3 and "JJ" in items[1] :
        #    app.append(items[1])
    #return len(app)

def multitag(ss,lang="en"):
    ss=".\n".join([re.sub("\\s+"," ",x) for x in ss])
    print(len(ss))
    temp=[]
    for el in tag(ss,lang):
        if el[0].startswith("<ttpw:"):
            if temp:
                yield temp[:]
                temp=[]
        else:
            temp.append(el)
    if temp:
        yield temp[:]

def count_ADJ(ss):
    for f in multitag(ss):
        app=list()
        for items in f:
            if len(items)==3 and "JJ" in items[1] :
                app.append(items[1])
        yield len(app)


if __name__ == '__main__':
    print(math.log(10))
    testo = """As well as concluding authorities had twice violated her right to a fair trial, the ECHR also found they had failed to investigate her complaints she had been subjected to degrading treatment, including being slapped on the head and deprived of sleep. The court did not, however, uphold her complaint of ill-treatment."""
    tag(testo)
    tag(testo)
    multitag(testo)
    count_ADJ(testo)
