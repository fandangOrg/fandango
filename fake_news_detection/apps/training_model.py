from ds4biz_predictor_core.factories.scikit_predictor_factories import TransformingPredictorFactory
from ds4biz_predictor_core.model.creation_requests import CreationRequest
from ds4biz_predictor_core.model.transformers.transformers import ColumnTransformer
from fake_news_detection.business.featureEngineering import add_new_features_to_df, preprocess_features_of_df
from fake_news_detection.config.MLprocessConfig import transforming_mapping, text_preprocessing_mapping, new_features_mapping, name_classifier, params_classifier
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath
from pandas import DataFrame, read_csv
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

class Train_model:
    def load_df(self,path_to_dataset:str, sample_size:float=0.05) -> DataFrame:
        df = read_csv(path_to_dataset, index_col=0)
        print("\n > load dataframe from \'", path_to_dataset, "\'" )
        if sample_size < 1.0:
            sample = df.sample(frac=sample_size)
            print("\n > sample (", sample_size, "%)", "[", sample.columns, "]")
            return sample
        else:
            return df
    
    
    def preprocess_df(self,training_set:DataFrame, path_for_store_preprocessed_df:str="./prova.csv", store:bool=True) -> DataFrame:
        training_set_modified = preprocess_features_of_df(df=training_set.dropna(), mapping=text_preprocessing_mapping)
        print("\n 1) Training_set_modified: \n", training_set_modified.iloc[0, :])
        training_set_improved = add_new_features_to_df(df=training_set_modified.dropna(), mapping=new_features_mapping)
        print("\n 2) Training_set_improved: \n", training_set_improved.iloc[0, :])
        training_set_final = training_set_improved.dropna()
        print("\n 3) Training_set_final: \n", training_set_final.iloc[0, :])
        if store:
            training_set_final.to_csv(path_for_store_preprocessed_df)
        return training_set_final
    
    
    def training(self,model_name:str, training_set_final, daopredictor):
        y = training_set_final['label']
        X = training_set_final.drop(['label'], axis=1)
        print("Shape of X:", X.shape)
        print("Columns of X:", X.columns)
        request_transformer = ColumnTransformer(transforming_mapping)
        request_model = CreationRequest(name_classifier, params_classifier)
        model = TransformingPredictorFactory().create(request_model, request_transformer)
        model.id = model_name
        model.fit(X, y)
        daopredictor.save(model)
        print("\n Training of '" + model_name + "': DONE")
        print("   - Accuracy:", model.predictor.accuracy)
        print("   - Precision:", model.predictor.precision)
        print("   - Recall:", model.predictor.recall)
        print("   - F-measure:",  2 * (model.predictor.precision * model.predictor.recall) / (model.predictor.precision + model.predictor.recall))
    
    
    def evaluate(self,model_name:str, test_set_final, daopredictor):
        y_test = test_set_final['label']
        X_test = test_set_final.drop(['label'], axis=1)
        model = daopredictor.get_by_id(model_name)
        y_pred = model.predict(X_test)
        print("\n Evaluation of \'" + model_name + "\' on " + str(len(y_test)) + " observations:")
        print("   - Accuracy:", accuracy_score(y_test, y_pred))
        print("   - Precision:", precision_score(y_test, y_pred, average='macro'))
        print("   - Recall:", recall_score(y_test, y_pred, average='macro'))
        print("   - F-measure:",  f1_score(y_test, y_pred, average='macro'))



if __name__ == '__main__':
    daopredictor = FSMemoryPredictorDAO(picklepath)

    ##### TRAINING #####

    # LOAD RAW TRAIN SET AND PREPROCESS IT #
    #training_set = load_df("/home/andrea/Scaricati/fandango_data.csv", sample_size=0.025)
    #training_set_final = preprocess_df(training_set, path_for_store_preprocessed_df="/home/andrea/Scaricati/fandango_data_preprocessed.csv", store=True)

    # LOAD ALREADY PREPROCESSED TRAIN SET #
    training_set_final = load_df("/home/andrea/Scaricati/fandango_data_preprocessed.csv", sample_size=1)
    print(training_set_final.columns)

    training("modello_en_all", training_set_final, daopredictor)


    ##### EVALUATION #####

    # LOAD RAW TEST SET AND PREPROCESS IT #
    #test_set = DAOTrainingPD().get_train_dataset(sample_size=1)
    #test_set_final = preprocess_df(test_set, path_for_store_preprocessed_df="/home/andrea/Scaricati/fandango_test_preprocessed.csv", store=True)

    # LOAD ALREADY PREPROCESSED TEST SET #
    test_set_final = load_df("/home/andrea/Scaricati/fandango_test_preprocessed_all.csv", sample_size=1)
    print(test_set_final.columns)

    evaluate("modello_en_all", test_set_final, daopredictor)
