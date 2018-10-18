'''
Created on 17 ott 2018

@author: camila
'''
from fake_news_detection.utils.DataPrep import DataPrep
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np
#import re
import itertools



class model(object):
    '''
    mechanism to buid and test a model and provide a possible prediction
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        
    
        self.DataPrep = DataPrep()
    
    def plot_confusion_matrix(self,cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap = plt.cm.get_cmap('Purples')):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)
    
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')
    
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, cm[i, j],
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
    
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.show()
        
    def BNclassifier(self, tfidf_train,tfidf_test,y_train,y_test):
        
        
        
        clf = MultinomialNB(alpha= 0.05)
        clf.fit(tfidf_train, y_train)
        pred = clf.predict(tfidf_test)
        score = metrics.accuracy_score(y_test, pred)
        print("Multinomial NB accuracy:   %0.4f" % score)
        cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
        self.plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
        
    def RFclassifier(self, tfidf_train,tfidf_test,y_train,y_test):
        '''Train'''
        rlf = RandomForestClassifier(n_jobs=2, random_state=1234,n_estimators=1000,max_depth=100)
    
        rlf.fit(tfidf_train, y_train)
        pred = rlf.predict(tfidf_test)
        score = metrics.accuracy_score(y_test, pred)
        print("Random Forest classifier accuracy :   %0.4f" % score)
        cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
        self.plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
        
    
    
            
        
                
                
        
if __name__  == "__main__":
    
    m = model()
    
    m.DataPrep.printInfodb()
    df_p = m.DataPrep.preprocessingdb()
    X_train, X_test, y_train, y_test = m.DataPrep.splitdataset(df_p)
    tfidf_train,tfidf_test,y_train,y_test = m.DataPrep.vectorizetfidf(X_train, X_test, y_train, y_test)
    #m.BNclassifier(tfidf_train, tfidf_test, y_train, y_test)
    m.RFclassifier(tfidf_train, tfidf_test, y_train, y_test)   
        
        
        
        