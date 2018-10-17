from _operator import itemgetter
from nltk.stem.snowball import SnowballStemmer
import nltk
#nltk.download('all')
import numpy 
from sklearn.feature_extraction.text import CountVectorizer
import treetaggerwrapper
class LemmaTokenizer(object): 
    
    def __init__(self):
        self.tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR="/home/camila/treetagger",TAGPARFILE="/home/camila/Downloads/treetagger/english-bnc-utf8.par"  )                                            
        self.tagger.tag_text("doc")
         
    def __call__(self, doc):  
        tokens = []
        #print(doc)
        for t in self.tagger.tag_text(doc):
            tt = t.split('\t')
            if len(tt)>2:
                if len(tt[2])<3:continue
                if not tt[2].startswith("replace"):
                    if tt[1].startswith( 'NO' ) or tt[1].startswith( 'AD' ) or tt[1].startswith( 'VE' ):
                        tokens.append(tt[2])
        return tokens
   
   
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
    print(tokenizer("hi i am "))