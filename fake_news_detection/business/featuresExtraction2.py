from polyglot.text import Text
from abc import ABC, abstractmethod
from fake_news_detection.config.constants import LANG_SUPPORTED
import numpy as np
from math import log
from string import punctuation
from nltk.corpus import stopwords
#from sklearn.feature_extraction import stop_words
from fake_news_detection.utils.SyllabCount import syllcounten
import string 
from itertools import count
from fake_news_detection.utils.DataPrep import clean_text
from fake_news_detection.utils.TreeTaggerConf import LemmaTokenizer
import treetaggerwrapper


class FeaturesExtractor(ABC):
    
    def __init__(self, lang:str):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__
        
    @abstractmethod
    def __call__(self, text:str) -> int:
        pass

class StopwordCounter(FeaturesExtractor):
    def __call__(self, text:str) -> int:
        try:
            doc = Text(text, hint_language_code=self.lang)
            stopWords = set(stopwords.words('english'))
            count = 0
            for word in doc.words:
                if word in stopWords:
                    count += 1
            return count 
        except:
            return np.nan


class LexicalDiversity(FeaturesExtractor):
    def __call__(self, txt:str) -> float:
        try:
            print(txt)
            doc = Text(txt, hint_language_code=self.lang)
            print(doc) 
            return (len(set(doc.words)) / len(doc.words))
        except:
            return np.nan
            
    
       
class AveWordxParagraph(FeaturesExtractor):
    def __call__(self,txt:str) -> float:
        try:
            
            x = txt.split('.\n\n')
            list_word_par = []
            translator = str.maketrans('', '', string.punctuation)
            print(len(x)) 
            #print(len(x))
            for parag in x:
                parag = parag.translate(translator)
                parag = parag.strip().split()
                count_word = 0
                for word in range(0,len(parag)):
                    count_word = word
            
                list_word_par.append(count_word)
        
            #print(np.mean(list_word_par))
            return(np.mean(list_word_par))
        except:
            return np.nan
                
            
class FleschReadingEase(FeaturesExtractor):
    def __call__(self, txt:str)  -> float:
        try:
            doc = Text(txt, hint_language_code=self.lang)
            tot_syl = 0
            
            for word in doc.words:
                c = syllcounten(word)
                tot_syl += c
            
            #print('total  vowels :',tot_syl)
            total_words = len(doc.words)
            if len(doc.sentences) != 0 and total_words != 0:
                ratio1 = total_words / len(doc.sentences)
                ratio2 = tot_syl / total_words
            
                return (206.835 - (1.015*ratio1) - (84.6*ratio2))
        except:
            return np.nan     
                
class FKGRadeLevel(FeaturesExtractor):
    def __call__(self, txt:str)  -> float:
        try:
            doc = Text(txt, hint_language_code=self.lang)
            tot_syl = 0
            
            for word in doc.words:
                c = syllcounten(word)
                tot_syl += c
            
            #print('total  vowels :',tot_syl)
            total_words = len(doc.words)
            if len(doc.sentences) != 0 and total_words != 0:
                ratio1 = total_words / len(doc.sentences)
                ratio2 = tot_syl / total_words
            
                return ((0.39*ratio1)+(11.8*ratio2)-15.59)
        except: 
            return np.nan


#da implementare bene    
class GunningFog(FeaturesExtractor):
    def __call__(self, txt:str)  -> float:
        
        doc = Text(txt, hint_language_code=self.lang)
        tot_syl = 0
        
        for word in doc.words:
            c = syllcounten(word)
            tot_syl += c
        
        print('total  syllabes :',tot_syl)
        total_words = len(doc.words)
        ratio1 = total_words / len(doc.sentences)
        ratio2 = tot_syl / total_words
        
        return (206.835 - (1.015*ratio1) - (84.6*ratio2))
          
          

    
    
class PunctuationCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            count = 0
            for p in punctuation:
                if p in text:
                    count += 1
            return log(count + 1)
        except:
            return np.nan


class CharsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            return log(len(text) + 1)
        except:
            return np.nan


class WordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for word in doc.words]) + 1)
        except:
            return np.nan


class SentencesCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            return log(len([sentence for sentence in doc.sentences]) + 1)
        except:
            return np.nan


class PositiveWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == 1]) + 1)
        except:
            return np.nan


class NegativeWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == -1]) + 1)
        except:
            return np.nan


class SentimentWordsCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            pos = 0
            neg = 0
            for word in doc.words:
                if word.polarity == +1:
                    pos += 1
                elif word.polarity == -1:
                    neg += 1
            return log(pos+1) - log(neg+1)
        except:
            return np.nan


class EntitiesCounter(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len(doc.entities) + 1)
        except:
            return np.nan
        
        
class CountAdj(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang, TAGDIR="/home/camila/TreeTag",TAGPARFILE="/home/camila/TreeTag/lib/english.par")                                            
            tagger.tag_text("doc")
            #print(tagger)
            count = 0 
            for tag in tagger.tag_text(text):
                tt = tag.split('\t')
                if tt[1] == 'JJ' or tt[1] == 'JJR' or tt[1] == 'JJS':
                    count += 1
          
            return count
        except:
            return np.nan
                
class CountAdv(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang, TAGDIR="/home/camila/TreeTag",TAGPARFILE="/home/camila/TreeTag/lib/english.par")                                            
            tagger.tag_text("doc")
            count = 0 
            adv_list_tag = ['RB', 'RBR', 'RBS', 'WRB']
            for tag in tagger.tag_text(text):
                tt = tag.split('\t')
                #print(tt)
                if tt[1] in adv_list_tag:
                    count += 1
          
            return count
        except:
            return np.nan
            
        
class CountPrep_conj(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang, TAGDIR="/home/camila/TreeTag",TAGPARFILE="/home/camila/TreeTag/lib/english.par")                                            
            tagger.tag_text("doc")
            count = 0 
            for tag in tagger.tag_text(text):
                tt = tag.split('\t')
                #print(tt)
                if tt[1] == 'IN' or tt[1] == "CC":
                    count += 1
          
            return count
        except:
            return np.nan
        
class countVerbs(FeaturesExtractor):
    def __call__(self, text:str) -> float:
        try:
            tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang, TAGDIR="/home/camila/TreeTag",TAGPARFILE="/home/camila/TreeTag/lib/english.par")                                            
            tagger.tag_text("doc")
            count = 0 
            verbs_list = ["VB","VBD","VBG","VBN","VBZ","VBP","VD","VDD","VDG","VDN","VDZ","VDP","VHD","VHG","VHN","VHZ","VHP","VV","VVD","VVG","VVN","VVZ","VVP"]
            for tag in tagger.tag_text(text):
                tt = tag.split('\t')
                #print(tt)
                if tt[1] in verbs_list:
                    count += 1
          
            return count
        except:
            return np.nan
        

           
        
if __name__ == "__main__":
    #l = StopwordCounter(lang='en')
    #print(l('hi, how are you? and you me feel for the fine and and and for then at at '))
    #s = AveWordxParagraph(lang = 'en')
    d = countVerbs(lang = 'en')
    print(d('stop please to dance be follow done come '))
   
    
    