'''
Created on Oct 18, 2018

@author: daniele
'''
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer,\
    CountVectorizer
from fake_news_detection.utils.DataPrep import clean_text
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
from fake_news_detection.config.AppConfig import dataset_beta
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline, make_union
from scipy import hstack
import numpy
import scipy.sparse as sp
from fake_news_detection.dao.PickleDao import ModelDao
from fake_news_detection.dao.TrainingDao import get_train_dataset
from fake_news_detection.business.FeaturesExtraction import features_extraction,\
    count_no_alfanumber, len_words, len_sentences, SampleExtractor,\
    DataFrameColumnExtracter
from sklearn.model_selection._split import train_test_split
from sklearn import metrics
from fake_news_detection.utils.Analyzer import display_scores
 
  
class SklearnModel:
    def __init__(self,model,name):
        self.model = model
        self.vect  = TfidfVectorizer(stop_words='english',ngram_range=(2,3))
        self.vect_title  = TfidfVectorizer(stop_words='english',ngram_range=(1,2))
        self.vects_features_title=[len]
        self.vects_features_text=[len,count_no_alfanumber]
        self.name=name
        
       
    def train_new(self,title_train,tfidf_train,y_train,df):
        print("df=",df.shape,df.columns)
        title_pipe = make_pipeline(
               DataFrameColumnExtracter('title'), 
               self.vect_title
        )
        
        text_pipe = make_pipeline(
               DataFrameColumnExtracter('text'), 
               self.vect
        )
        self.feature_union = make_union(title_pipe, text_pipe)
        sparse_matrix_of_counts = self.feature_union.fit_transform(df)
        self.model.fit(sparse_matrix_of_counts, y_train)
        
    def train(self,df,y_train):
        print("df=",df.shape,df.columns)
        title_pipe = make_pipeline(
               DataFrameColumnExtracter('title'), 
               self.vect_title
        )
        
        text_pipe = make_pipeline(
               DataFrameColumnExtracter('text'), 
               self.vect
        )
        #=======================================================================
        # self.feats_title= [('title', SampleExtractor('title', TfidfVectorizer(stop_words='english',ngram_range=(1,2))))]
        # self.feats_text= [('text',  SampleExtractor('text', TfidfVectorizer(stop_words='english',ngram_range=(1,2))))]
        #=======================================================================
        #=======================================================================
        # self.feats_title= [('title', SampleExtractor('title',self.vect_title))]
        # self.feats_text= [('text',  SampleExtractor('text',self.vect))]
        #=======================================================================
        self.feats_title=[]
        self.feats_text=[]
        df=features_extraction(df, self.vects_features_title, 'title')
        id_feats=0
        for col in df.columns:
            if col.startswith('new_f_title'):
                self.feats_title.append((str(id_feats),SampleExtractor(col)))
                id_feats+=1
        #
        df=features_extraction(df, self.vects_features_text, 'text')
        for col in df.columns:
            if col.startswith('new_f_text'):
                self.feats_text.append((str(id_feats),SampleExtractor(col)))
                id_feats+=1
        print("CREA PIPELINE")
        print(self.feats_title)
        if len(self.feats_title)>0:
            union_tl= FeatureUnion(self.feats_title)
            union_text= FeatureUnion(self.feats_text)
            self.feature_union = make_union(*[text_pipe,title_pipe,union_tl, union_text])
        else:
            self.feature_union = make_union(*[text_pipe,title_pipe])
        matrix=self.feature_union.fit_transform(df)
        print("feature_union" ,matrix.shape)    
        self.model.fit(matrix, y_train)

#===============================================================================
#         print("INIT TRAIN")
#         print(len(df),df.shape,df.columns)
#         #=======================================================================
#         matrix_text=self.union_text.fit_transform(df)
#         matrix_title =self.union_tl.fit_transform(df)
#         
#         
#         #=======================================================================
#         #=======================================================================
#         # matrix_text=self.vect.fit_transform(tfidf_train)
#         # matrix_title =self.vect_title.fit_transform(title_train)
#         #=======================================================================
#         print(matrix_text.shape)
#         print(matrix_title.shape)
# 
#         matrix=self._concatenate_csc_matrices_by_columns(matrix_text,matrix_title)
#         print(matrix.shape)
#===============================================================================

        #=======================================================================
        # self.model.fit(matrix, y_train)
        #=======================================================================
        #=======================================================================
        # terms = self.vect.get_feature_names()
        # vamx=display_scores(self.vect, matrix_text)
        #=======================================================================
            
    def analyzer_vector(self,values):
        vect= TfidfVectorizer(stop_words='english',ngram_range=(1,1))
        print("INIT TRAIN")
        matrix_text=vect.fit_transform(values)
        display_scores(vect, matrix_text)
        
        
    def _concatenate_csc_matrices_by_columns(self,matrix1, matrix2):
        combined_2 = sp.hstack([matrix1,matrix2],format='csr')    
        return combined_2

    def predict_accuary(self,X_test, y_test):
        df=features_extraction(X_test, self.vects_features_title, 'title')
        df=features_extraction(df, self.vects_features_text, 'text')

        #matrix=self.vect.transform(X_test['text'])
        #matrix_title =self.vect_title.transform(X_test['title'])
        #matrix=self._concatenate_csc_matrices_by_columns(matrix,matrix_title)
        matrix=self.feature_union.transform(df)
        pred=self.model.predict(matrix)
        score = metrics.accuracy_score(y_test['label'], pred)
        print(score)
        
    def predict(self,title,text):
        doc = {"title":[title],"text":[text]}
        df=pd.DataFrame.from_dict(doc)
        df=features_extraction(df, self.vects_features_title, 'title')
        df=features_extraction(df, self.vects_features_text, 'text')
        print("PREDICT",df)
        matrix=self.feature_union.transform(df)
        print(self.model.predict(matrix))
        return pd.DataFrame(self.model.predict_proba(matrix), columns=self.model.classes_)

        #=======================================================================
        # print("title:",title)
        # #text = clean_text(text)
        # text = text
        # print("text:",text)
        # matrix = self.vect.transform([text])
        # matrix_title = self.vect_title.transform([title])
        # matrix=self._concatenate_csc_matrices_by_columns(matrix,matrix_title)
        # print(self.model.predict(matrix))
        # return pd.DataFrame(self.model.predict_proba(matrix), columns=self.model.classes_)
        #=======================================================================
        
    def partial_fit(self,title,text,label):
        doc = {"title":[title],"text":[text]}
        df=pd.DataFrame.from_dict(doc)
        df=features_extraction(df, self.vects_features_title, 'title')
        df=features_extraction(df, self.vects_features_text, 'text')
        print("PARTIAL")
        print("title:",title)
        print("text:",text)
        print("label:",label)
        matrix=self.feature_union.transform(df)
        print(matrix.shape)
        #=======================================================================
        # matrix = self.vect.transform([text])
        # matrix_title = self.vect_title.transform([title])
        # matrix=self._concatenate_csc_matrices_by_columns(matrix,matrix_title)
        #=======================================================================
        
        print(self.model.partial_fit(matrix,[label]))
        print("FITTATO")
        #ModelDao().save(self,self.name)
        
        
    def most_informative_feature_for_binary_classification(self, n=100):  
        class_labels = self.model.classes_
        feature_names = self.vect .get_feature_names()
        topn_class1 = sorted(zip(self.model.coef_[0], feature_names))[:n]
        topn_class2 = sorted(zip(self.model.coef_[0], feature_names))[-n:]    
        for coef, feat in topn_class1:
            print(class_labels[0], coef, feat)   
            print()    
        for coef, feat in reversed(topn_class2):
            print(class_labels[1], coef, feat)
            
                                                                                                

if __name__ == '__main__':
    #clf = MultinomialNB(alpha= 0.05)
    oo = ModelDao()
#    clf = RandomForestClassifier(n_jobs=-1, n_estimators=1,max_depth=40)
    clf = MultinomialNB(alpha= 0.05)

    model=SklearnModel(clf,'test')
    training_set=get_train_dataset()
    app_fake_text=training_set[training_set['label']=="FAKE"]['text']
    app_real_text=training_set[training_set['label']=="REAL"]['text']
    
    #===========================================================================
    # print("REAL")
    # model.analyzer_vector(app_real_text)
    # print("FAKE")
    # model.analyzer_vector(app_fake_text)
    #===========================================================================
    
    
    X_train, X_test, y_train, y_test = train_test_split(training_set[['title','text']],training_set[["label"]], test_size=0.33, random_state=42)
    print(y_train)
#    model.train(X_train['title'],X_train['text'], y_train['label'],X_train)
    model.train(X_train, y_train['label'])

    #model.train(training_set['title'],training_set['text'], training_set['label'],training_set)
    oo.save(model,model.name)
    #
    model = oo.load('test')
    model.predict_accuary(X_test,y_test)
#===============================================================================
#     print(model.predict("GOOGLE IS NOW","""Google Pinterest Digg Linkedin Reddit Stumbleupon Print Delicious Pocket Tumblr 
# There are two fundamental truths in this world: Paul Ryan desperately wants to be president. And Paul Ryan will never be president. Today proved it. 
# In a particularly staggering example of political cowardice, Paul Ryan re-re-re-reversed course and announced that he was back on the Trump Train after all. This was an aboutface from where he was a few weeks ago. He had previously declared he would not be supporting or defending Trump after a tape was made public in which Trump bragged about assaulting women. Suddenly, Ryan was appearing at a pro-Trump rally and boldly declaring that he already sent in his vote to make him President of the United States. It was a surreal moment. The figurehead of the Republican Party dosed himself in gasoline, got up on a stage on a chilly afternoon in Wisconsin, and lit a match. . @SpeakerRyan says he voted for @realDonaldTrump : “Republicans, it is time to come home” https://t.co/VyTT49YvoE pic.twitter.com/wCvSCg4a5I 
# — ABC News Politics (@ABCPolitics) November 5, 2016 
# The Democratic Party couldn’t have asked for a better moment of film. Ryan’s chances of ever becoming president went down to zero in an instant. In the wreckage Trump is to leave behind in his wake, those who cravenly backed his campaign will not recover. If Ryan’s career manages to limp all the way to 2020, then the DNC will have this tape locked and loaded to be used in every ad until Election Day. 
# The ringing endorsement of the man he clearly hates on a personal level speaks volumes about his own spinelessness. Ryan has postured himself as a “principled” conservative, and one uncomfortable with Trump’s unapologetic bigotry and sexism. However, when push came to shove, Paul Ryan – like many of his colleagues – turned into a sniveling appeaser. After all his lofty tak about conviction, his principles were a house of cards and collapsed with the slightest breeze. 
# What’s especially bizarre is how close Ryan came to making it through unscathed. For months the Speaker of the House refused to comment on Trump at all. His strategy seemed to be to keep his head down, pretend Trump didn’t exist, and hope that nobody remembered what happened in 2016. Now, just days away from the election, he screwed it all up. 
# If 2016’s very ugly election has done any good it’s by exposing the utter cowardice of the Republicans who once feigned moral courage. A reality television star spit on them, hijacked their party, insulted their wives, and got every last one of them to kneel before him. What a turn of events. 
# Featured image via Twitter"""))
#===============================================================================

    