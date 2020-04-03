import pandas
from fake_news_detection.dao.DAO import FSMemoryPredictorDAO
from fake_news_detection.config.AppConfig import picklepath, resources_path, \
    resources_path_train
from lightgbm.sklearn import LGBMClassifier
from fake_news_detection.model.predictor import Preprocessing, FakePredictor, \
    KerasFakePredictor, VotingClassifierPredictor, BERTFakePredictor, \
    BertPreprocessing, BERTFakePredictorWithStyleBase
from keras.wrappers.scikit_learn import KerasClassifier
from fake_news_detection.test.keras_no_deep import create_model1
import torch
from pytorch_pretrained_bert.modeling import BertForPreTraining
from bert.modeling import BertModel
import torch.nn as nn
import matplotlib.pyplot as plt
from fake_news_detection.business.featureEngineeringDeepL import FeaturesEngineering
from fake_news_detection.config.constants import N_FEATURES_STYLE
from fake_news_detection.business.ModelDeepLearning import BertStyleAndTextFeatures


class BertForMultiClass(BertForPreTraining):
    
    def __init__(self, config, num_labels):
        super(BertForMultiClass, self).__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, num_labels)
        # self.apply(self.init_weights)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None, head_mask=None):
        outputs = self.bert(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits
    
    
def training_model_LGBMClassifier(lang, X, X_test=None, draw=False):
    daopredictor = FSMemoryPredictorDAO(picklepath)
    predictor = LGBMClassifier(boosting_type='gbdt',
                               num_leaves=100,
                               max_depth=-1,
                               learning_rate=0.1,
                               n_estimators=200,
                               n_jobs=-1) 
    print("crea modello")
    model = FakePredictor(predictor=predictor, preprocessing=Preprocessing(lang), id=lang)
    columns = model.fit(X, X_test)
    X = X.drop(['text'], axis=1)
    X = X.drop(['title'], axis=1)
    X = X.drop(['label'], axis=1)
    if draw:
        """ Plot the significance scores of feautures """
        print(model.predictor.feature_importances_)
        feat_imp = pandas.Series(model.predictor.feature_importances_, index=columns)
        # feat_imp = pd.Series(self.mdl.models[0].feature_importances_, index=X.columns)
        feat_imp.nlargest(50).plot(kind='barh', figsize=(8, 10))
        plt.tight_layout()
        plt.show()
        plt.close()
    
    daopredictor.save(model)


def training_model_KerasClassifier(lang, X):
    input_dim = X.shape[1] - 3
    epochs = 100
    batch_size = int(8507 / 20) + 1

    daopredictor = FSMemoryPredictorDAO(picklepath)
    predictor = KerasClassifier(build_fn=create_model1, input_dim=input_dim, epochs=epochs, batch_size=batch_size, verbose=1) 
    print("crea modello")
    model = KerasFakePredictor(predictor=predictor, preprocessing=Preprocessing(lang), id=lang)
    model.fit(X)
    daopredictor.save(model)


def training_model_VotingClassifier(lang, X):
    daopredictor = FSMemoryPredictorDAO(picklepath)
    print("crea modello")
    model = VotingClassifierPredictor(preprocessing=Preprocessing(lang), id=lang)
    model.fit(X)
    daopredictor.save(model)


def build_model_BERT(name="model_3"):
    daopredictor = FSMemoryPredictorDAO(picklepath)
    print("crea modello")
    model = BERTFakePredictor(torch.load(picklepath + "/" + name), preprocessing=BertPreprocessing(), id='all')
    daopredictor.save(model, id='all')

    
def train_model_BERT_stylebase(name,X):
    model = BertStyleAndTextFeatures.from_pretrained("bert-base-multilingual-uncased" ,num_labels=2,device='cuda',features_style_number=N_FEATURES_STYLE)
    predictor=BERTFakePredictorWithStyleBase(model,FeaturesEngineering(),name,device=model.device)
    predictor.fit(X, y=None)
if __name__ == '__main__':
    #build_model_BERT()
    
    # for lang,train in [('it','default_train_domains_text_it.csv'),('nl','default_train_domains_text_nl.csv'),('es','default_train_domains_text_es.csv')]:
   # for lang, train in [('en', 'default_train_domains_text_en.csv'), ('it', 'default_train_domains_text_it.csv'), ('nl', 'default_train_domains_text_nl.csv'), ('es', 'default_train_domains_text_es.csv')]:
     for lang,train in [('en','default_train_v3_only_kaggle_new_features_text_en.csv')]:
        print("leggi train")
        X = pandas.read_csv(resources_path + "/" + train).iloc[:, 1:]
        X=X.sample(100)
        X['label'] = X['label'].map({0: "FAKE", 1: "GOOD"})
        X['label'] = X['label'].map({"FAKE":0,"GOOD":1})
        # ##
        append=False
        if append:
            if lang == "en":
                #SE USIAMO L'INGLESE APPENDEVA ANCHE KAGGLE OLTRE QUELLO DAI DOMINI
                X_test = pandas.read_csv(resources_path + "/default_train_v3_only_kaggle_new_features_text_en.csv").iloc[:, 1:]
                X_test['label'] = X_test['label'].map({0: "FAKE", 1: "GOOD"})
                print(len(X))
                X = X.append(X_test)
                print(len(X))
        train_model_BERT_stylebase("bert_"+lang,X)   
        #training_model_LGBMClassifier(lang, X)
        print("---")
