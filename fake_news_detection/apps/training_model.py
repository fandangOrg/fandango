import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from fake_news_detection.business.configurationModel import create_trasformer_predictor
from fake_news_detection.business.featureEngineering import add_new_features_to_df,\
    Filter_Text
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD
from fake_news_detection.business.FeaturesExtraction import len_words,\
    count_no_alfanumber


#daopredictor=FSMemoryPredictorDAO(picklepath)

#DAOTrainingPD()
def training(model_name:str, training_set_improved,daopredictor):
    #training_set = dao_train.get_train_dataset(sample_size=sample_size)
    #training_set_improved = add_new_features_to_df(df=training_set)
    y = training_set_improved['label']
    X = training_set_improved.drop(['label'], axis=1)
    print("Shape of X:", X.shape)
    print("Columns of X:", X.columns)
    model = create_trasformer_predictor(name_classifier = "MultinomialNB",
                                        params_classifier = {'alpha':0.5},
                                        transformer_title = TfidfVectorizer(min_df=10, stop_words='english', lowercase=True),
                                        transformer_text = TfidfVectorizer(min_df=15, ngram_range=(2, 3), stop_words='english', lowercase=True))
    model.id = model_name
    model.fit(X, y)
    daopredictor.save(model)
    print("\n Training of '" + model_name + "': DONE")
    print("   - Accuracy:", model.predictor.accuracy)
    print("   - Precision:", model.predictor.precision)
    print("   - Recall:", model.predictor.recall)

#===============================================================================
# 
# def predict(nome_modello):
#     training_set = DAOTrainingPD().get_train_dataset(sample_size=0.05)
#     X = training_set[['title', 'text']]
#     prediction = daopredictor.get_by_id(nome_modello).predict(X)
#     print(prediction)
# 
# 
# def predict_proba(nome_modello):
#     training_set = DAOTrainingPD().get_train_dataset(sample_size=0.05)
#     X = training_set[['title', 'text']]
#     prob_distribution = daopredictor.get_by_id(nome_modello).predict_proba(X)
#     print(daopredictor.get_by_id(nome_modello).predictor.predictor.classes_)
#     np.set_printoptions(formatter={'float_kind': '{:f}'.format})
#     print(prob_distribution)
#===============================================================================


if __name__ == '__main__':
    daopredictor=FSMemoryPredictorDAO(picklepath)
    training_set = DAOTrainingPD().get_train_dataset(sample_size=1)
    #training_set_improved = add_new_features_to_df(df=training_set,mapping=[('title',Filter_Text(filter=["the"]))])
    training_set_improved = add_new_features_to_df(df=training_set,mapping=[('text', len_words), ('text', count_no_alfanumber), ('title', len_words), ('title', count_no_alfanumber),('text*',Filter_Text(filter=["the"]))])
    training_set_improved =training_set
    training("modello_en2",training_set_improved,daopredictor)
    #===========================================================================
    # predict("modello_en2")
    # predict_proba("modello_en2")
    #===========================================================================