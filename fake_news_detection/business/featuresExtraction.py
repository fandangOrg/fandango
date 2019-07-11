from polyglot.text import Text
from abc import ABC, abstractmethod
from fake_news_detection.config.constants import LANG_SUPPORTED
import numpy as np
from math import log
from string import punctuation
#from sklearn.feature_extraction import stop_words
from fake_news_detection.utils.SyllabCount import syllcounten, syllcountit
import string 
from itertools import count
from fake_news_detection.utils.DataPrep import clean_text
from fake_news_detection.test.singleton_filter import Singleton_Filter
import numpy

singleton=Singleton_Filter()
class FeaturesExtractor(ABC):
    
    def __init__(self, lang:str,**kwargs):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__
        
    @abstractmethod
    def __call__(self, text:str) -> int:
        pass

class FeaturesExtractorLanguageDependence(FeaturesExtractor):
    
    def __init__(self, lang:str,**kwargs):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__
        self._set_funct_by_lang()
        
    def _set_funct_by_lang(self):
        pass

    def __call__(self, text:str,**kwargs)  -> float:
        try:
            return  self.lang_to_funct[self.lang](text,**kwargs)
        except KeyError:
            raise ValueError("Invalid language!")
            


class StopwordCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> int:
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            stopWords = singleton.nlp_tool[self.lang+"_stopwords"]
            count = 0
            for word in doc.words:
                if word in stopWords:
                    count += 1
            return count/len(doc.words)
        except:
            return np.nan


class LexicalDiversity(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            #print(txt)
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            #print(doc) 
            return (len(set(doc.words)) / len(doc.words))
        except:
            return np.nan
            
    
       
class AveWordxParagraph(FeaturesExtractor):
    def __call__(self,txt:str,**kwargs) -> float:
        try:
            
            x = txt.split('.\n\n')
            list_word_par = []
            translator = str.maketrans('', '', string.punctuation)
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
                
            
class FleschReadingEase(FeaturesExtractorLanguageDependence):
        
    def _set_funct_by_lang(self):
        self.lang_to_funct={"it":self._it,
                            "en":self._en}
        
        
    def _it(self,text,**kwargs):
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            tot_syl = 0
            
            for word in doc.words:
                c = syllcountit(word)
                tot_syl += c
            
            #print('total  vowels :',tot_syl)
            total_words = len(doc.words)
            if len(doc.sentences) != 0 and total_words != 0:
                ratio1 = total_words / len(doc.sentences)
                ratio2 = tot_syl / total_words
            
                return (206.835 - (1.015*ratio1) - (84.6*ratio2))
        except:
            return np.nan    
        
    def _en(self,text,**kwargs):   
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
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
        
        
        
               
class FKGRadeLevel(FeaturesExtractorLanguageDependence):
    def _set_funct_by_lang(self):
        self.lang_to_funct={"it":self._it,
                            "en":self._en}
        
        
    def _en(self,text,**kwargs):   
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
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
        
    def _it(self,text,**kwargs):
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
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
    def __call__(self, text:str,**kwargs)  -> float:
        
        doc=kwargs.get('doc')
        if doc is None:
            doc = Text(text, hint_language_code=self.lang)
        tot_syl = 0
        
        for word in doc.words:
            c = syllcounten(word)
            tot_syl += c
        
        #print('total  syllabes :',tot_syl)
        total_words = len(doc.words)
        ratio1 = total_words / len(doc.sentences)
        ratio2 = tot_syl / total_words
        
        return (206.835 - (1.015*ratio1) - (84.6*ratio2))
          
          

    
    
class PunctuationCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            count = 0
            for p in text:   
                if p in punctuation:
                    count += 1
            return count/len(text)
        except:
            return np.nan


class CharsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            return log(len(text) + 1)
        except:
            return np.nan


class WordsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return log(len([word for word in doc.words]) + 1)
        except:
            return np.nan


class AVGWordsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            return len(text.split())/len(text) 
        except:
            return np.nan
        
class SentencesCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return log(len([sentence for sentence in doc.sentences]) + 1)
        except:
            return np.nan

class AVGSentencesSizeCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            doc=kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return numpy.mean([len(sentence.words) for sentence in doc.sentences])
        except:
            return np.nan
        
class PositiveWordsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == 1]) + 1)
        except:
            return np.nan


class NegativeWordsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == -1]) + 1)
        except:
            return np.nan


class SentimentWordsCounter(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        try:
            text = clean_text(text)
            doc=kwargs.get('doc')
            if doc is None:
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
    def __call__(self, text:str,**kwargs) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len(doc.entities) + 1)
        except:
            return np.nan
        
        
class CountAdj(FeaturesExtractor):
    def __call__(self, text:str, **kwargs) -> float:
        try:
            #tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang)
            tagger=singleton.nlp_tool[self.lang+"_tagger"]                                            
            #tagger.tag_text("doc")
            #print(tagger)
            tag_text=kwargs.get("tag_text")
            count = 0 
            if tag_text is None:
                tag_text = tagger.tag_text(text)
            for tag in tag_text:
                tt = tag.split('\t')
                if len(tt)>1:
                    if tt[1] == 'JJ' or tt[1] == 'JJR' or tt[1] == 'JJS':
                        count += 1
            if len(tag_text)==0: return 0.0
            return count/len(tag_text)
        except:
            return np.nan
                
class CountAdv(FeaturesExtractor):
    def __call__(self, text:str, **kwargs) -> float:
        #tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang)
        tagger=singleton.nlp_tool[self.lang+"_tagger"]                                    
        #tagger.tag_text("doc")
        count = 0 
        adv_list_tag = ['RB', 'RBR', 'RBS', 'WRB']
        tag_text=kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            tt = tag.split('\t')
            if len(tt)>1:
                #print(tt)
                if tt[1] in adv_list_tag:
                    count += 1
        if len(tag_text)==0: return 0.0
        return count/len(tag_text)
            
        
class CountPrep_conj(FeaturesExtractor):
    def __call__(self, text:str, **kwargs) -> float:
        tagger=singleton.nlp_tool[self.lang+"_tagger"]
        #tagger.tag_text("doc")
        count = 0 
        tag_text=kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            tt = tag.split('\t')
            #print(tt)
            if len(tt)>1:
                if tt[1] == 'IN' or tt[1] == "CC":
                    count += 1
        if len(tag_text)==0: return 0.0
        return count/len(tag_text)
        
class countVerbs(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        tagger=singleton.nlp_tool[self.lang+"_tagger"]
        #tagger.tag_text("doc")
        count = 0 
        verbs_list = ["VB","VBD","VBG","VBN","VBZ","VBP","VD","VDD","VDG","VDN","VDZ","VDP","VHD","VHG","VHN","VHZ","VHP","VV","VVD","VVG","VVN","VVZ","VVP"]
        tag_text=kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            tt = tag.split('\t')
            if len(tt)>1:
                if tt[1] in verbs_list:
                    count += 1
        if len(tag_text)==0: return 0.0
        return count/len(tag_text)
        
class POSDiversity(FeaturesExtractor):
    def __call__(self, text:str,**kwargs) -> float:
        tagger=singleton.nlp_tool[self.lang+"_tagger"]
        #tagger.tag_text("doc")
        count = 0 
        tag_text=kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        tags=[]
        for tag in tag_text:
            tt = tag.split('\t')
            if len(tt)>1:
                #print(tt)
                tags.append(tt[1]) 
        if len(tags)==0: return 0.0
        return len(set(tags))/58
    
    
class Multifunction(FeaturesExtractor):
    
    def __init__(self,functions,lang:str):
        self.functions=functions
        self.__name__ = [f.__name__ for f in functions]
        self.i=0
        self.lang=lang
        
        
    def __call__(self, text:str) -> list:
        self.i+=1
        if self.i % 500==0:
            print(self.i)
        #text = clean_text(text)
        results=list()
        tagger=singleton.nlp_tool[self.lang+"_tagger"]
        ##tagger.tag_text("doc")
        tag_text = tagger.tag_text(text)
        doc = Text(text, hint_language_code=self.lang)
        for f in self.functions:
            #start = time.time()
            results.append(f(text, **{"tag_text":tag_text,"doc":doc}))
            #end = time.time()
            #print(f,end - start)
        #print("................................................")
        return results           
        
        
if __name__ == "__main__":
    
    l=FleschReadingEase('en')
    print(l('hi, how are you? and you me feel for the fine and and and for then at at '))
    #l = StopwordCounter(lang='en')
    #print(l('hi, how are you? and you me feel for the fine and and and for then at at '))
    #s = AveWordxParagraph(lang = 'en')
    #===========================================================================
    # d = countVerbs(lang = 'en')
    # print(d('stop please to dance be follow done come '))
    # d = POSDiversity(lang = 'en')
    # print(d('stop please to dance be follow done come '))
    # 
    # doc = Text('''The json representation of this blob.
    # .. versionchanged:: 0.5.1
    #     Made ``json`` a property instead of a method to restore backwards
    #     compatibility that was broken after version 0.4.0.''', hint_language_code='en')
    # total_sentence=len(doc.sentences)
    # print(total_sentence)
    # for sentence in doc.sentences:
    #     print(sentence)
    # print(numpy.mean([len(sentence.words) for sentence in doc.sentences]))
    #===========================================================================
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    