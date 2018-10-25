'''
Created on 26 set 2018

@author: camila
'''
import pandas as pd
from fake_news_detection.config.AppConfig import dataset_beta
training_set= pd.read_csv(dataset_beta+"/") # dataset
