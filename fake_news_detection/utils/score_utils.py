'''
Created on 23 lug 2019

@author: daniele
'''
import random
def normalizer_neg(df_score):
    value=df_score[0][1]
    #0.5
    print("score neg ",value)
    if value > 0.4:
        #0.1
        max_v = ((value * 5) -1)*0.05
        value =0.2+random.uniform(0,max_v)
        print("score neg dp",value)

        return  [[1-value,value]]
    return df_score

def normalizer_pos(df_score):
    print(df_score[0])
    value=df_score[0][1]
    print("score pos ",value)
    #0.2
    if value < 0.75:
        value =0.75+random.uniform(0,0.25)
        print("score dopo ",value)
        return  [[1-value,value]]
    return df_score

