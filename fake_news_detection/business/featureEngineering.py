from typing import List, Tuple
from pandas.core.frame import DataFrame
from uuid import uuid4
from fake_news_detection.business.FeaturesExtraction import len_words, count_no_alfanumber
import pandas as pd
import nltk
from nltk.stem.api import StemmerI
from nltk.stem.snowball import ItalianStemmer
from nltk.stem import snowball


class ColumnFEExtractor:
    def __init__(self, mapping: List[Tuple]):
        self.mapping = mapping

    def __call__(self, objects):
        if isinstance(objects, DataFrame):
            for couple in self.mapping:
                col = couple[0]
                fun = couple[1]
                objects[col + "_" + getfunctionname(fun)] = objects[col].apply(fun)
            return objects
        else:
            ret = []
            for obj in objects:
                obj = dict(obj)
                for couple in self.mapping:
                    col = couple[0]
                    fun = couple[1]
                    value = obj.get(col)
                    if value:
                        obj[col + "_" + getfunctionname(fun)] = fun(obj[col])
                ret.append(obj)
            return ret


def getfunctionname(f):
    if f.__name__ == "<lambda>":
        return str(uuid4())
    else:
        return f.__name__

class Features_text_enginee:
    def __init__(self):
        self.__name__="unknown"
        
     
    
    
class Filter_Text(Features_text_enginee):
    def __init__(self,filter:List[str]):
        super().__init__()
        self.__name__="filter_list"
        self.filter_words=filter
        
    def __call__(self,text):
        new_text = " ".join([word for word in text.split() if word.lower() not in self.filter_words])
        return new_text
    
    
        
def add_new_features_to_df(df:DataFrame, mapping:List[Tuple]=[('text', len_words), ('text', count_no_alfanumber), ('title', len_words), ('title', count_no_alfanumber)] ) -> DataFrame:
    extractor = ColumnFEExtractor(mapping)
    df_improved = extractor(df)
    return df_improved



### EXAMPLE ###
# if __name__ == "__main__":
#
#     dicts = [{"a": 1, "b": 2, "d": "sdsadasd", "c": "222"},
#              {"a": 2, "d": "sdsd,sdasds,saddsa", "c": "dsdsf"},
#              {"c": "sadadsdsaxcc", "d": "sdsdsd,,sss"}]
#     df = pd.DataFrame(dicts)
#     print(df)
#
#     def incrementa(x):
#         return x + 1
#
#     def numvirg(x):
#         return x.count(",")
#
#     extractor = ColumnFEExtractor({"a": lambda x: x + 1, "b": incrementa, "c": len, "d": numvirg})
#     print(extractor(df))
#     print(extractor(dicts))
