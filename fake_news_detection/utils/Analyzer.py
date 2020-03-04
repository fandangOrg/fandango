'''
Created on Oct 26, 2018

@author: daniele
'''
import numpy as np


def display_scores(vectorizer, tfidf_result):
    # http://stackoverflow.com/questions/16078015/
    vmax = dict()
    scores = zip(vectorizer.get_feature_names(),
                 np.asarray(tfidf_result.sum(axis=0)).ravel())
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    for k, item in enumerate(sorted_scores):
        if k > 100:break
        vmax[item[0]] = item[1]
        print ("{0:50} Score: {1}".format(item[0], item[1]))
    return vmax
        
