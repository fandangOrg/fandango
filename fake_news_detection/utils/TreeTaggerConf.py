from _operator import itemgetter
from nltk.stem.snowball import SnowballStemmer
import nltk
#nltk.download('all')
import numpy 
from sklearn.feature_extraction.text import CountVectorizer
import treetaggerwrapper
from fake_news_detection.utils.DataPrep import clean_text

class LemmaTokenizer(object): 
    
    def __init__(self):
        self.tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')                             
        
        self.tagger.tag_text("doc")
         
    def __call__(self, doc):  
        taggers = []
        for t in self.tagger.tag_text(doc):
            tt = t.split('\t')
            print(tt)
            taggers.append(tt)
        return taggers
   
   
tokenizerClass=LemmaTokenizer()   

def tokenizer(sentence):
    try:
        vect = CountVectorizer(tokenizer=tokenizerClass,token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b',analyzer= 'word',stop_words = SnowballStemmer("english",ignore_stopwords=True).stopwords, ngram_range=(1,1))
        words = list()
        data=vect.fit_transform([sentence]).toarray()
        dist = numpy.sum(data, axis=0)
        vocab = vect.get_feature_names()
        
        for tag, count in sorted(zip(vocab, dist),key=itemgetter(1)):
            for i in range(0,count):
                words.append(tag)
        return words
    except ValueError:
        return []    
 
if __name__ == '__main__':
    print(tokenizerClass("you me damn so please stop sweet clown sad kind soft better happier"))
    
    
    
    