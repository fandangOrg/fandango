from typing import List, Tuple
from pandas.core.frame import DataFrame
from uuid import uuid4
from _collections import defaultdict
import pandas
from fake_news_detection.business.featuresExtraction import Multifunction


class ColumnFEExtractor:
    def __init__(self, mapping: List[Tuple]):
        self.mapping = mapping


    def _multi_function(self):
        column_to_fun=defaultdict(list)
        for couple in  self.mapping:
            col = couple[0]
            fun = couple[1]
            lang=fun.lang
            #print("-->",col,fun)
            column_to_fun[col].append(fun)
            
        for col in column_to_fun:
            #print(col,column_to_fun[col])
            yield col,Multifunction(column_to_fun[col],lang) 
            
            
            
    def __call__(self, objects, cmd:bool=0):
        if isinstance(objects, DataFrame):
            if cmd == 1:
                for col,fun in self._multi_function():
                    try:
                        print("analisi",col)
                        s = objects[col].apply(fun)
                        names = fun.__name__
                        df=pandas.DataFrame.from_items(zip(s.index, s.values) )
                        df=df.T
                        df.columns =[col+"_"+name for name in names]
                        objects=pandas.concat([df, objects], axis=1, sort=False)
                        print(object)
                        #objects[[col+"_"+name for name in names]]=values
                    except KeyError as e :
                        print(e)
                        continue
                return  objects  
                    
            for couple in self.mapping:
                col = couple[0]
                fun = couple[1]
                if cmd == 0:
                    values = objects[col].apply(fun)
                    objects[col + "_" + self.__getfunctionname(fun)] = values  # Add new column
                else:
                    values = objects[col].apply(fun)
                    objects[col] = values                                      # Modify the same column
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
                        if cmd == 0:
                            obj[col + "_" + self.__getfunctionname(fun)] = fun(obj[col])  #Add new column
                        else:
                            obj[col] = fun(obj[col])  #Modify the same column
                ret.append(obj)
            return ret

    def __getfunctionname(self, f):
        if f.__name__ == "<lambda>":
            return str(uuid4())
        else:
            return f.__name__



def add_new_features_to_df(df:DataFrame, mapping:List[Tuple]) -> DataFrame:
    extractor = ColumnFEExtractor(mapping)
    df_improved = extractor(df, 1)
#    df_improved.dropna(inplace=True)
    return df_improved



def preprocess_features_of_df(df:DataFrame, mapping:List[Tuple]) -> DataFrame:
    extractor = ColumnFEExtractor(mapping)
    df_modified = extractor(df, 1)
    df_modified.dropna(inplace=True)
    return df_modified




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
