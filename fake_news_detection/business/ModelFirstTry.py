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
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
 


class Model(object):
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
        rlf = RandomForestClassifier(n_jobs=-1, random_state=1234,n_estimators=1000,max_depth=100)
    
        rlf.fit(tfidf_train, y_train)
        pred = rlf.predict(tfidf_test)
        score = metrics.accuracy_score(y_test, pred)
        print("Random Forest classifier accuracy :   %0.4f" % score)
        cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
        self.plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
        
    
    def RFclassifier_(self, tfidf_train,y_train):
        
        '''Train'''
        rlf = RandomForestClassifier(n_jobs=2, random_state=1234,n_estimators=1000,max_depth=100)
    
        rlf_fitted = rlf.fits(tfidf_train, y_train)
        
        return rlf_fitted
        
        
    def RF_score(self,rlf_fitted,tfidf_test,y_test):
        
        pred = rlf_fitted.predict(tfidf_test)
        score = metrics.accuracy_score(y_test, pred)
        print("Random Forest classifier accuracy :   %0.4f" % score)
        cm = metrics.confusion_matrix(y_test, pred, labels=['FAKE', 'REAL'])
        self.plot_confusion_matrix(cm, classes=['FAKE', 'REAL'])
    
    def RF_prediction(self,rlf_fitted, singleSample):
        
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
        text = DataPrep.clean_text(singleSample)
        vec_sample = tfidf_vectorizer.transform(text)
        pred_sample = rlf_fitted.predict(vec_sample)
        
        print(pred_sample)
        
    
        
    
        
        
        
    
    #def RFclassifier_pred(self):
            
    #def RFclassifier_pred(self):
            
        
                
                
        
if __name__  == "__main__":
    
    m = Model()
    
    m.DataPrep.printInfodb()
    df_p = m.DataPrep.preprocessingdb()
    X_train, X_test, y_train, y_test = m.DataPrep.splitdataset(df_p)
    tfidf_train,tfidf_test,y_train,y_test = m.DataPrep.vectorizetfidf(X_train, X_test, y_train, y_test)
    #m.BNclassifier(tfidf_train, tfidf_test, y_train, y_test)
    rlf_fitted = m.RFclassifier_(tfidf_train, y_train)
    m.RF_score(rlf_fitted, tfidf_test, y_test)
    m.RF_prediction(rlf_fitted, """Google Pinterest Digg Linkedin Reddit Stumbleupon Print Delicious Pocket Tumblr 
There are two fundamental truths in this world: Paul Ryan desperately wants to be president. And Paul Ryan will never be president. Today proved it. 
In a particularly staggering example of political cowardice, Paul Ryan re-re-re-reversed course and announced that he was back on the Trump Train after all. This was an aboutface from where he was a few weeks ago. He had previously declared he would not be supporting or defending Trump after a tape was made public in which Trump bragged about assaulting women. Suddenly, Ryan was appearing at a pro-Trump rally and boldly declaring that he already sent in his vote to make him President of the United States. It was a surreal moment. The figurehead of the Republican Party dosed himself in gasoline, got up on a stage on a chilly afternoon in Wisconsin, and lit a match. . @SpeakerRyan says he voted for @realDonaldTrump : “Republicans, it is time to come home” https://t.co/VyTT49YvoE pic.twitter.com/wCvSCg4a5I 
— ABC News Politics (@ABCPolitics) November 5, 2016 
The Democratic Party couldn’t have asked for a better moment of film. Ryan’s chances of ever becoming president went down to zero in an instant. In the wreckage Trump is to leave behind in his wake, those who cravenly backed his campaign will not recover. If Ryan’s career manages to limp all the way to 2020, then the DNC will have this tape locked and loaded to be used in every ad until Election Day. 
The ringing endorsement of the man he clearly hates on a personal level speaks volumes about his own spinelessness. Ryan has postured himself as a “principled” conservative, and one uncomfortable with Trump’s unapologetic bigotry and sexism. However, when push came to shove, Paul Ryan – like many of his colleagues – turned into a sniveling appeaser. After all his lofty tak about conviction, his principles were a house of cards and collapsed with the slightest breeze. 
What’s especially bizarre is how close Ryan came to making it through unscathed. For months the Speaker of the House refused to comment on Trump at all. His strategy seemed to be to keep his head down, pretend Trump didn’t exist, and hope that nobody remembered what happened in 2016. Now, just days away from the election, he screwed it all up. 
If 2016’s very ugly election has done any good it’s by exposing the utter cowardice of the Republicans who once feigned moral courage. A reality television star spit on them, hijacked their party, insulted their wives, and got every last one of them to kneel before him. What a turn of events. 
Featured image via Twitter""")
        
        