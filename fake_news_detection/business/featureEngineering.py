from typing import List, Tuple
from pandas.core.frame import DataFrame
from uuid import uuid4
import swifter


class ColumnFEExtractor:
    def __init__(self, mapping: List[Tuple]):
        self.mapping = mapping

    def __call__(self, objects, cmd:bool=0):
        if isinstance(objects, DataFrame):
            for couple in self.mapping:
                col = couple[0]
                fun = couple[1]
                print("applico ",couple,fun)
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
    df_improved = extractor(df, 0)
    df_improved.dropna(inplace=True)
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
