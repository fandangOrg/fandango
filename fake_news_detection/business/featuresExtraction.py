from polyglot.text import Text
from abc import ABC, abstractmethod
from fake_news_detection.config.constants import LANG_SUPPORTED
import numpy as np
from math import log
from string import punctuation
# from sklearn.feature_extraction import stop_words
from fake_news_detection.utils.SyllabCount import syllcounten, syllcountit
import string 
from itertools import count
#from fake_news_detection.utils.DataPrep import clean_text
from fake_news_detection.test.singleton_filter import Singleton_Filter
import numpy
from textstat.textstat import textstat, textstatistics
from builtins import ZeroDivisionError
from scipy.constants.constants import pt

singleton = Singleton_Filter()


class utils_senteces(textstatistics):

    def __init__(self, lang):
        super(utils_senteces, self).__init__()
        self.lang = lang
    
    def syllable_count(self, text):
        return textstat.syllable_count(text, lang=self.lang)

    def all_analysis(self, text):
        try:
            v = self.lix(text)
        except ZeroDivisionError:
            v = 0.0
        analysis = {
        "rix":self.rix(text),
        "lix":v,
        "gunning_fog":self.gunning_fog(text),
        "dale_chall_readability_score":self.dale_chall_readability_score(text),
        "linsear_write_formulas":self.linsear_write_formula(text),
        "automated_readability_index":self.automated_readability_index(text),
        "coleman_liau_index":self.coleman_liau_index(text),
        "smog_index":self.smog_index(text),
        "flesch_kincaid_grade":self.flesch_kincaid_grade(text),
        "vflesch_reading_ease":self.flesch_reading_ease(text),
        "avg_sentence_per_word":self.avg_sentence_per_word(text),
        "avg_letter_per_word":self.avg_letter_per_word(text),
        "avg_character_per_word":self.avg_character_per_word(text),
        "avg_syllables_per_word":self.avg_syllables_per_word(text),
        "avg_sentence_length":self.avg_sentence_length(text)
        }
        return analysis

        
class FeaturesExtractor(ABC):
    
    def __init__(self, lang:str, **kwargs):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__
        
    @abstractmethod
    def __call__(self, text:str) -> int:
        pass


class FeaturesExtractorLanguageDependence(FeaturesExtractor):
    
    def __init__(self, lang:str, **kwargs):
        self.lang = lang
        if self.lang not in LANG_SUPPORTED:
            raise ValueError("Invalid language!")
        self.__name__ = self.__class__.__name__
        self._set_funct_by_lang()
        
    def _set_funct_by_lang(self):
        pass

    def __call__(self, text:str, **kwargs) -> float:
        try:
            return  self.lang_to_funct[self.lang](text, **kwargs)
        except KeyError:
            raise ValueError("Invalid language!")


class StopwordCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> int:
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            stopWords = singleton.nlp_tool[self.lang + "_stopwords"]
            count = 0
            for word in doc.words:
                if word in stopWords:
                    count += 1
            return count / len(doc.words)
        except:
            return 0.0


class LexicalDiversity(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            # print(txt)
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            # print(doc) 
            return (len(set(doc.words)) / len(doc.words))
        except:
            return 0.0
    
       
class AveWordxParagraph(FeaturesExtractor):

    def __call__(self, txt:str, **kwargs) -> float:
        try:
            
            x = txt.split('.\n\n')
            list_word_par = []
            translator = str.maketrans('', '', string.punctuation)
            # print(len(x))
            for parag in x:
                parag = parag.translate(translator)
                parag = parag.strip().split()
                count_word = 0
                for word in range(0, len(parag)):
                    count_word = word
            
                list_word_par.append(count_word)
        
            # print(np.mean(list_word_par))
            return(np.mean(list_word_par))
        except:
            return 0.0
                
            
class FleschReadingEase(FeaturesExtractorLanguageDependence):
        
    def _set_funct_by_lang(self):
        self.lang_to_funct = {"it":self._score,
                            "en":self._score,
                            "es":self._score,
                            "nl":self._score}
        
    def _score(self, text, **kwargs):  
        try:
                return utils_senteces(self.lang).flesch_reading_ease(text)
        except: 
            return 0.0
        
    #===========================================================================
    # def _it(self,text,**kwargs):
    #     try:
    #         doc=kwargs.get('doc')
    #         if doc is None:
    #             doc = Text(text, hint_language_code=self.lang)
    #         tot_syl = 0
    #         
    #         for word in doc.words:
    #             c = syllcountit(word)
    #             tot_syl += c
    #         
    #         #print('total  vowels :',tot_syl)
    #         total_words = len(doc.words)
    #         
    #         if len(doc.sentences) != 0 and total_words != 0:
    #             ratio1 = total_words / len(doc.sentences)
    #             ratio2 = tot_syl / total_words
    #         
    #             return (206.835 - (1.015*ratio1) - (84.6*ratio2))
    #         
    #     except:
    #         return 0.0    
    #     
    # def _en(self,text,**kwargs):   
    #     try:
    #         doc=kwargs.get('doc')
    #         if doc is None:
    #             doc = Text(text, hint_language_code=self.lang)
    #         tot_syl = 0
    #         
    #         for word in doc.words:
    #             c = syllcounten(word)
    #             tot_syl += c
    #         
    #         #print('total  vowels :',tot_syl)
    #         total_words = len(doc.words)
    #         print(self._score(text))
    #         if len(doc.sentences) != 0 and total_words != 0:
    #             ratio1 = total_words / len(doc.sentences)
    #             ratio2 = tot_syl / total_words
    #         
    #             return (206.835 - (1.015*ratio1) - (84.6*ratio2))
    #     except:
    #         return 0.0    
    #     
    #===========================================================================
        
               
class FKGRadeLevel(FeaturesExtractorLanguageDependence):

    def _set_funct_by_lang(self):
        self.lang_to_funct = {"it":self._it,
                            "en":self._en,
                            "es":self._score,
                            "nl":self._score}
        
    def _score(self, text, **kwargs):  
        try:
                return utils_senteces(self.lang).flesch_kincaid_grade(text)
        except: 
            return 0.0
    
    def _en(self, text, **kwargs):   
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            tot_syl = 0
            
            for word in doc.words:
                c = syllcounten(word)
                tot_syl += c
            
            # print('total  vowels :',tot_syl)
            print(self._score(text))
            total_words = len(doc.words)
            if len(doc.sentences) != 0 and total_words != 0:
                ratio1 = total_words / len(doc.sentences)
                ratio2 = tot_syl / total_words
            
                return ((0.39 * ratio1) + (11.8 * ratio2) - 15.59)
        except: 
            return 0.0
        
    def _it(self, text, **kwargs):
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            tot_syl = 0
            
            for word in doc.words:
                c = syllcounten(word)
                tot_syl += c
            
            # print('total  vowels :',tot_syl)
            total_words = len(doc.words)
            if len(doc.sentences) != 0 and total_words != 0:
                ratio1 = total_words / len(doc.sentences)
                ratio2 = tot_syl / total_words
            
                return ((0.39 * ratio1) + (11.8 * ratio2) - 15.59)
        except: 
            return 0.0


# da implementare bene    
class GunningFog(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        
        doc = kwargs.get('doc')
        if doc is None:
            doc = Text(text, hint_language_code=self.lang)
        tot_syl = 0
        
        for word in doc.words:
            c = syllcounten(word)
            tot_syl += c
        
        # print('total  syllabes :',tot_syl)
        total_words = len(doc.words)
        ratio1 = total_words / len(doc.sentences)
        ratio2 = tot_syl / total_words
        
        return (206.835 - (1.015 * ratio1) - (84.6 * ratio2))
    
    
class PunctuationCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            count = 0
            for p in text:   
                if p in punctuation:
                    count += 1
            return count / len(text)
        except:
            return 0.0


class CharsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            return log(len(text) + 1)
        except:
            return 0.0


class WordsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return log(len([word for word in doc.words]) + 1)
        except:
            return 0.0


class AVGWordsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            return len(text.split()) / len(text) 
        except:
            return 0.0

        
class SentencesCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return log(len([sentence for sentence in doc.sentences]) + 1)
        except:
            return 0.0


class AVGSentencesSizeCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            return numpy.mean([len(sentence.words) for sentence in doc.sentences])
        except:
            return 1.0

        
class PositiveWordsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == 1]) + 1)
        except:
            return 0.0


class NegativeWordsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            text = clean_text(text)
            doc = Text(text, hint_language_code=self.lang)
            return log(len([word for sentence in doc.sentences for word in sentence.words if word.polarity == -1]) + 1)
        except:
            return 0.0


class SentimentWordsCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            text = clean_text(text)
            doc = kwargs.get('doc')
            if doc is None:
                doc = Text(text, hint_language_code=self.lang)
            pos = 0
            neg = 0
            for word in doc.words:
                if word.polarity == +1:
                    pos += 1
                elif word.polarity == -1:
                    neg += 1
            return log(pos + 1) - log(neg + 1)
        except:
            return 0.0


class EntitiesCounter(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            doc = Text(text, hint_language_code=self.lang)
            return log(len(doc.entities) + 1)
        except:
            return 0.0
        
        
class CountAdj(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        try:
            # tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang)
            tagger = singleton.nlp_tool[self.lang + "_tagger"]                                            
            # tagger.tag_text("doc")
            # print(tagger)
            adj_list_tag = ["JJ", "JJR", "JJS", "adj", "ADJ", 'adjabbr']
            tag_text = kwargs.get("tag_text")
            count = 0 
            if tag_text is None:
                tag_text = tagger.tag_text(text)
            for tag in tag_text:
                tt = tag.split('\t')
                if len(tt) > 1:
                    if tt[1] in adj_list_tag:
                        count += 1
            if len(tag_text) == 0: return 0.0
            return count / len(tag_text)
        except:
            return 0.0

                
class CountAdv(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        # tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.lang)
        tagger = singleton.nlp_tool[self.lang + "_tagger"]                                    
        # tagger.tag_text("doc")
        count = 0 
        adv_list_tag = ['RB', 'RBR', 'RBS', 'WRB', "ADV", "adv", "advabbr"]
        tag_text = kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            # print(tag)
            tt = tag.split('\t')
            if len(tt) > 1:
                if tt[1] in adv_list_tag:
                    count += 1
        if len(tag_text) == 0: return 0.0
        return count / len(tag_text)
            
        
class CountPrep_conj(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        tagger = singleton.nlp_tool[self.lang + "_tagger"]
        # tagger.tag_text("doc")
        count = 0 
        prep_list_tag = ['IN', 'CC', 'prep'"prepabbr", "PRE", "PREP"]

        tag_text = kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            tt = tag.split('\t')
            # print(tt)
            if len(tt) > 1:
                if tt[1] in prep_list_tag:
                    count += 1
        if len(tag_text) == 0: return 0.0
        return count / len(tag_text)

        
class countVerbs(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        tagger = singleton.nlp_tool[self.lang + "_tagger"]
        # tagger.tag_text("doc")
        count = 0 
        verbs_list = ["VB", "VBD", "VBG", "VBN", "VBZ", "VBP", "VD", "VDD", "VDG", "VDN", "VDZ", "VDP", "VHD", "VHG", "VHN", "VHZ", "VHP", "VV", "VVD", "VVG", "VVN", "VVZ", "VVP"]
        tag_text = kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
        for tag in tag_text:
            tt = tag.split('\t')
            if len(tt) > 1:
                if tt[1] in verbs_list or tt[1][0].lower() == "v":
                    count += 1
        if len(tag_text) == 0: return 0.0
        return count / len(tag_text)

        
class POSDiversity(FeaturesExtractor):

    def __call__(self, text:str, **kwargs) -> float:
        tagger = singleton.nlp_tool[self.lang + "_tagger"]
        # tagger.tag_text("doc")
        count = 0 
        tag_text = kwargs.get("tag_text")
        if tag_text is None:
            tag_text = tagger.tag_text(text)
            
        tags = []
        for tag in tag_text:
            tt = tag.split('\t')
            if len(tt) > 1:
                # print(tt)
                tags.append(tt[1]) 
        if len(tags) == 0: return 0.0
         # nl-->https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/dutch-tagset.txt
         # it --> http://sslmit.unibo.it/~baroni/collocazioni/itwac.tagset.txt
         # spanish -> Source: http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/spanish-tagset.txt
        n_tag = {'it':52, 'en':58, 'nl':41, 'es':75}
        return len(set(tags)) / n_tag[self.lang]
    
    
class Multifunction(FeaturesExtractor):
    
    def __init__(self, functions, lang:str):
        self.functions = functions
        self.__name__ = [f.__name__ for f in functions]
        self.i = 0
        self.lang = lang
        
    def __call__(self, text:str) -> list:
        self.i += 1
        if self.i % 500 == 0:
            print(self.i)
        # text = clean_text(text)
        results = list()
        tagger = singleton.nlp_tool[self.lang + "_tagger"]
        # #tagger.tag_text("doc")
        tag_text = tagger.tag_text(text)
        doc = Text(text, hint_language_code=self.lang)
        all_analysis = utils_senteces(self.lang).all_analysis(text)
        for f in self.functions:
            x = f.__name__
            value = all_analysis.get(x)
            
            if value is not None:
                # value=(x,all_analysis.get(x))
                results.append(value)
            else:
            # start = time.time()
                # results.append((f.__name__,f(text, **{"tag_text":tag_text,"doc":doc})))
                results.append(f(text, **{"tag_text":tag_text, "doc":doc}))
            # end = time.time()
            # print(f,end - start)
        # print("................................................")
        return results           
        
        
if __name__ == "__main__":
    lang_code = 'it'
        
    analisi = [('text', AVGSentencesSizeCounter(lang=lang_code)),
    ('title', CountAdv(lang=lang_code)),
    ('text', CountAdv(lang=lang_code)),
    ('title', StopwordCounter(lang=lang_code)),
    ('text', LexicalDiversity(lang=lang_code)),
    ('text', FleschReadingEase(lang=lang_code)),
    ('text', FKGRadeLevel(lang=lang_code)),
    ('text', POSDiversity(lang=lang_code)),
    ]
    text = "o you happen to know the library, AllenNLP? If you’re working on Natural Language Processing (NLP), you might hear about the name. However, I guess a few people actually use it. Or the other has tried before but hasn’t know where to start because there are lots of functions. For those who aren’t familiar with…"
    for a, analyzer in analisi:
        print(analyzer.__name__)
        print(analyzer.__name__, analyzer(text))
                                    
    #===========================================================================
    # 
    # l=FleschReadingEase('en')
    # print(l('hi, how are you? and you me feel for the fine and and and for then at at '))
    #===========================================================================
    # l = StopwordCounter(lang='en')
    # print(l('hi, how are you? and you me feel for the fine and and and for then at at '))
    # s = AveWordxParagraph(lang = 'en')
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
    
    
