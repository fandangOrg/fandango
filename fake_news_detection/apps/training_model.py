from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory
from ds4biz_predictor_core.model.creation_requests import CreationRequest
from ds4biz_predictor_core.model.transformers.transformers import ColumnTransformer
from fake_news_detection.business.featureEngineering import add_new_features_to_df, preprocess_features_of_df
from fake_news_detection.config.MLprocessConfig import transforming_mapping, name_classifier_1, params_classifier_1, text_preprocessing_mapping, new_features_mapping, name_classifier_2, params_classifier_2
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from fake_news_detection.dao.TrainingDAO import DAOTrainingPD
from pandas import DataFrame



def preprocess_df(training_set:DataFrame) -> DataFrame:
    training_set_modified = preprocess_features_of_df(df=training_set.dropna(), mapping=text_preprocessing_mapping)
    print("\n 1) Training_set_modified: \n", training_set_modified.iloc[0, :])
    training_set_improved = add_new_features_to_df(df=training_set_modified.dropna(), mapping=new_features_mapping)
    print("\n 2) Training_set_improved: \n", training_set_improved.iloc[0, :])
    training_set_final = training_set_improved.dropna()
    print("\n 3) Training_set_final: \n", training_set_final.iloc[0, :])
    return training_set_final



def training(model_name:str, training_set_final, daopredictor):
    y = training_set_final['label']
    X = training_set_final.drop(['label'], axis=1)
    print("Shape of X:", X.shape)
    print("Columns of X:", X.columns)
    request_transformer = ColumnTransformer(transforming_mapping)
    request_model = CreationRequest(name_classifier_2, params_classifier_2)
    model = TransformingPredictorFactory().create(request_model, request_transformer)
    model.id = model_name
    model.fit(X, y)
    daopredictor.save(model)
    print("\n Training of '" + model_name + "': DONE")
    print("   - Accuracy:", model.predictor.accuracy)
    print("   - Precision:", model.predictor.precision)
    print("   - Recall:", model.predictor.recall)



if __name__ == '__main__':
    daopredictor = FSMemoryPredictorDAO(picklepath)
    daotrainingset = DAOTrainingPD()
    training_set = daotrainingset.get_train_dataset(sample_size=0.05)
    training_set_final = preprocess_df(training_set)
    training("modello_en_all", training_set_final, daopredictor)
