import spacy
import os
import pandas as pd
from helper import helper
from langdetect import detect
from helper import config as cfg
from flair.models import SequenceTagger
from flair.data import Sentence
from helper.helper import (extract_publisher_info,
                           create_websites_db)


class DataPreprocessing:
    def __init__(self):
        self.raw_data = None
        self.preprocessed_data = None
        self.default_field = cfg.default_field
        self.lang_model = None
        self.websites_list = None
        self.ner_library = cfg.ner_library
        self.ner_model_name = None
        self.ner_model = None
        self.countries_website = cfg.countries_websites
        self.csv_filepath = os.path.join(cfg.resources_dir, cfg.csv_filepath)

    def retrieve_list_of_websites(self):
        try:
            self.websites_list = create_websites_db(filepath=self.csv_filepath,
                                                    countries=self.countries_website)

        except Exception as e:
            cfg.logger.error(e)
        return self

    def init_ner_models(self, lang_model):
        try:
            self.lang_model = lang_model
            self.ner_model_name = self.select_ner_model()
            self.ner_model = self.load_ner_model(ner_library=self.ner_library,
                                                 ner_model_name=self.ner_model_name)
        except Exception as e:
            cfg.logger.error(e)

    def select_ner_model(self):
        ner_model_name = None
        try:
            if self.ner_library == "spacy":
                ner_model_name = self.select_spacy_model(lang_model=self.lang_model)
            elif self.ner_library == "flair":
                ner_model_name = self.select_flair_model(lang_model=self.lang_model)
            else:
                cfg.logger.warning("Unvalid NER library.")
        except Exception as e:
            cfg.logger.error(e)
        return ner_model_name

    @staticmethod
    def select_spacy_model(lang_model):
        model_name = None
        try:
            if lang_model=='en':
                model_name = 'en_core_web_sm'
            elif lang_model =='it':
                model_name = 'it_core_news_sm'
            elif lang_model =='de':
                model_name = 'de_core_news_sm'
            elif lang_model =='es':
                model_name = 'es_core_news_sm'
            elif lang_model =='nl':
                model_name = 'xx_ent_wiki_sm' #'nl_core_news_sm'
            elif lang_model == 'el':
                model_name = 'el_core_news_sm'
            elif lang_model =='xx':
                model_name = 'xx_ent_wiki_sm'
            else:
                cfg.logger.warning("Unable language in Spacy Package. Multilanguage model will be used")
                model_name = 'xx_ent_wiki_sm'
        except Exception as e:
            cfg.logger.error(e)
        return model_name

    @staticmethod
    def select_flair_model(lang_model):
        model_name = None
        try:
            if lang_model == 'en':
                model_name = 'ner'
            elif lang_model == 'de':
                model_name = 'de-ner'
            elif lang_model == 'nl':
                model_name = 'nl-ner'
            elif lang_model == 'fr':
                model_name = 'fr-ner'
            elif lang_model == 'xx':
                model_name = 'ner-multi'
            else:
                cfg.logger.warning("Unable language in Flair Package. Multilanguage model will be used")
                model_name = 'ner-multi'
        except Exception as e:
            cfg.logger.error(e)
        return model_name

    @staticmethod
    def load_ner_model(ner_library, ner_model_name):
        ner_model = None
        try:
            if ner_library == "spacy":
                ner_model = spacy.load(ner_model_name)
            elif ner_library == "flair":
                ner_model = SequenceTagger.load(ner_model_name)
            else:
                cfg.logger.warning("Unvalid Spacy Model")
        except Exception as e:
            cfg.logger.error(e)
        return ner_model

    @staticmethod
    def detect_language(text):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language code detected
        # =================================================
        lang = None
        try:
            if len(text)>5 and text != '':
                lang = detect(text)
        except Exception as e:
            cfg.logger.error(e)
        return lang

    @staticmethod
    def ner_analysis(ner_library, ner_model, text):
        ner_analysis_data = None
        try:
            if ner_library == "spacy":
                ner_data = ner_model(text.title())
                #ner_data = ner_model(text)
                if len(ner_data.ents) > 0:
                    for ent in ner_data.ents:
                        cfg.logger.warning(ent.label_)
                        if ent.label_ == 'PER' or ent.label_ == 'PERSON':
                            ner_analysis_data = str(ent)
            elif ner_library == "flair":
                sentence = Sentence(text.title())
                ner_model.predict(sentence)
                for ent in sentence.get_spans("ner"):
                    if ent.tag == 'PER':
                        ner_analysis_data = ent.text
            else:
                cfg.logger.warning("Unvalid NER library.")
        except Exception as e:
            cfg.logger.error(e)
        return ner_analysis_data

    @staticmethod
    def remove_line_breaks(text):
        preprocessed_text = None
        try:
            preprocessed_text = text.replace("\r", "").replace("\n", "")
        except Exception as e:
            cfg.logger.error(e)
        return preprocessed_text

    def preprocess_author_name(self, author_name, ner_library="spacy", ner_model=None,
                               min_char=2):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language code detected
        # =================================================
        author_name_cleaned = None
        try:
            # 2) Named Entity Recognition
            author_name_cleaned = self.ner_analysis(ner_library=ner_library, ner_model=ner_model,
                                                    text=author_name)

        except Exception as e:
            cfg.logger.error(e)
        return author_name_cleaned

    @staticmethod
    def extract_publisher_information(source_domain, list_of_websites=None, threshold=95):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language code detected
        # =================================================
        publisher_info = None
        try:
            publisher_info = extract_publisher_info(source_domain, list_of_websites=list_of_websites,
                                                    threshold=threshold)
        except Exception as e:
            cfg.logger.error(e)
        return publisher_info

    @staticmethod
    def get_unique_values(data, fuzzy=True, fuzzy_threshold=.8):
        unique_data = []
        try:
            if isinstance(data, list):
                unique_data = helper.remove_duplicate_strings_from_list(str_lst=data, fuzzy=fuzzy,
                                                                        fuzzy_threshold=fuzzy_threshold)
            else:
                unique_data = data
        except Exception as e:
            cfg.logger.error(e)
        return unique_data

    def apply_preprocessing(self, data, manual_annot=False):
        try:
            # Check input structure
            if isinstance(data, dict):
                features = self.required_cols(manual_annot=manual_annot)
                # All the required features are available
                if not features >= data.keys():
                    # 1) Detect language and init NER
                    data["language"] = self.detect_language(text=data["text"])
                    self.init_ner_models(lang_model=data["language"])

                    # 2) Cleaning authors
                    cleaned_authors = [self.preprocess_author_name(author_name=i,
                                                                   ner_library=self.ner_library,
                                                                   ner_model=self.ner_model) for i in data["authors"]]
                    data["authors"] = self.get_unique_values(data=cleaned_authors, fuzzy=False,
                                                             fuzzy_threshold=.8)
                    # 3) Retrieving publisher name
                    if self.websites_list is None:
                        self.websites_list = pd.read_csv(self.csv_filepath, index_col=0)

                    publisher_info = self.extract_publisher_information(source_domain=data["source_domain"],
                                                                        list_of_websites=self.websites_list,
                                                                        threshold=82)


                    data["publisher"] = publisher_info["name"]
                    data["country"] = publisher_info["country"]
                    data["nationality"] = publisher_info["nationality"]

        except Exception as e:
            cfg.logger.error(e)
        return data

    @staticmethod
    def required_cols(manual_annot=False):
        features = {}
        try:
            if not manual_annot:
                features = {"authors", "date_created", "date_modified", "date_published", "description","identifier",
                            "images", "keywords", "language", "publish_date_estimated", "source_domain", "summary",
                            "text", "texthash", "title", "top_image", "url", "videos"}
            else:
                features = {"authors", "title", "text", "url"}
        except Exception as e:
            cfg.logger.error(e)
        return features