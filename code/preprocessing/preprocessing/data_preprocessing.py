import spacy
import os
import pandas as pd
from helper import helper
from langdetect import detect
from helper import global_variables as gv
from flair.models import SequenceTagger
from flair.data import Sentence
from helper.helper import (extract_publisher_info, create_websites_db,
                           retrieve_image_by_url, filter_by_size,
                           filter_by_aspect_ratio, remove_non_alphabetical_symbols)
from models.preprocessing_models import PreprocessingOutputDocument


class DataPreprocessing:
    def __init__(self):
        self.raw_data = None
        self.preprocessed_data = None
        self.default_field = gv.default_field
        self.lang_model = None
        self.websites_list = None
        self.ner_library = gv.ner_library
        self.ner_model_name = None
        self.ner_model = None
        self.countries_website = gv.countries_websites
        self.csv_filepath = os.path.join(gv.resources_dir, gv.csv_filepath)

    def retrieve_list_of_websites(self):
        try:
            self.websites_list = create_websites_db(filepath=self.csv_filepath,
                                                    countries=self.countries_website)

        except Exception as e:
            gv.logger.error(e)

    def init_ner_models(self, lang_model):
        try:
            self.lang_model = lang_model
            self.ner_model_name = self.select_ner_model()
            self.ner_model = self.load_ner_model(ner_library=self.ner_library,
                                                 ner_model_name=self.ner_model_name)
        except Exception as e:
            gv.logger.error(e)

    def select_ner_model(self):
        ner_model_name = None
        try:
            if self.ner_library == "spacy":
                ner_model_name = self.select_spacy_model(lang_model=self.lang_model)
            elif self.ner_library == "flair":
                ner_model_name = self.select_flair_model(lang_model=self.lang_model)
            else:
                gv.logger.warning("Unvalid NER library.")
        except Exception as e:
            gv.logger.error(e)
        return ner_model_name

    @staticmethod
    def select_spacy_model(lang_model):
        model_name = None
        try:
            if lang_model == 'en':
                model_name = 'en_core_web_sm'
            elif lang_model == 'it':
                model_name = 'it_core_news_sm'
            elif lang_model == 'de':
                model_name = 'de_core_news_sm'
            elif lang_model == 'es':
                model_name = 'es_core_news_sm'
            elif lang_model == 'nl':
                model_name = 'nl_core_news_sm'
            elif lang_model == 'el':
                model_name = 'el_core_news_sm'
            elif lang_model == 'xx':
                model_name = 'xx_ent_wiki_sm'
            else:
                gv.logger.warning("Unable language in Spacy Package. Multi-language model will be used")
                model_name = 'xx_ent_wiki_sm'
        except Exception as e:
            gv.logger.error(e)
        return model_name

    @staticmethod
    def select_flair_model(lang_model):
        model_name = None
        try:
            if lang_model == 'en':
                model_name = 'ner-fast'
            elif lang_model == 'de':
                model_name = 'de-ner'
            elif lang_model == 'nl':
                model_name = 'nl-ner-rnn'
            elif lang_model == 'fr':
                model_name = 'fr-ner'
            else:
                gv.logger.warning("Unable language in Flair Package. Multilingual model will be used")
                model_name = 'ner-fast'
        except Exception as e:
            gv.logger.error(e)
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
                gv.logger.warning("Invalid Model")
        except Exception as e:
            gv.logger.error(e)
        return ner_model

    @staticmethod
    def detect_language(data, key, min_char: int = 5):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language status detected
        # =================================================
        lang = None
        try:
            if len(data[key]) > min_char and data[key] != '':
                lang = detect(data[key])
        except Exception as e:
            gv.logger.error(e)
        return lang

    @staticmethod
    def ner_analysis(ner_library, ner_model, text):
        ner_analysis_data = None
        try:
            # Preprocess text
            text_filtered: str = remove_non_alphabetical_symbols(text=text)

            if ner_library == "spacy":
                ner_data = ner_model(text_filtered)
                if len(ner_data.ents) > 0:
                    for ent in ner_data.ents:
                        if ent.label_ == 'PER' or ent.label_ == 'PERSON':
                            ner_analysis_data = str(ent)
            elif ner_library == "flair":
                sentence = Sentence(text_filtered)
                ner_model.predict(sentence)
                for ent in sentence.get_spans("ner"):
                    if ent.tag == 'PER' and ent.score >= 0.80:
                        ner_analysis_data = ent.text
            else:
                gv.logger.warning("Unvalid NER library.")
        except Exception as e:
            gv.logger.error(e)
        return ner_analysis_data

    @staticmethod
    def remove_line_breaks(text):
        preprocessed_text = None
        try:
            preprocessed_text = text.replace("\r", "").replace("\n", "")
        except Exception as e:
            gv.logger.error(e)
        return preprocessed_text

    def preprocess_author_name(self, author_name, ner_library="spacy", ner_model=None):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language status detected
        # =================================================
        author_name_cleaned = None
        try:
            # 2) Named Entity Recognition
            author_name_cleaned = self.ner_analysis(ner_library=ner_library, ner_model=ner_model,
                                                    text=author_name)

        except Exception as e:
            gv.logger.error(e)
        return author_name_cleaned

    @staticmethod
    def extract_publisher_information(source_domain, list_of_websites=None, threshold=95):
        # ================================================
        # INPUT:
        #       - text: text
        # OUTPUT:
        #       - lang: Language status detected
        # =================================================
        publisher_info = None
        try:
            publisher_info = extract_publisher_info(source_domain, list_of_websites=list_of_websites,
                                                    threshold=threshold)
        except Exception as e:
            gv.logger.error(e)
        return publisher_info

    """"@staticmethod
    def retrieve_publisher_information(source_rank, url: str, language: str) -> dict:
        publisher_info: CategoryAnalysisDoc = object.__new__(CategoryAnalysisDoc)
        try:
            # 1. Retrieve information about source
            res_parser = source_rank.process_url(url=url)
            publisher_info: CategoryAnalysisDoc = source_rank.get_category_analysis(
                url=res_parser.domain, language=language)

        except Exception as e:
            gv.logger.error(e)
        return publisher_info.__dict__"""

    @staticmethod
    def remove_banner_images(images):
        filter_images = []
        try:
            for img_url in images:
                res = DataPreprocessing.filter_image_by_url(img_url)
                # Not filter case
                if not res:
                    filter_images.append(img_url)
            # Check uniqueness
            filter_images = list(set(filter_images))
        except Exception as e:
            gv.logger.error(e)
        return filter_images

    @staticmethod
    def get_unique_values(data, fuzzy: bool = True, fuzzy_threshold: float = 80):
        unique_data = []
        try:
            if isinstance(data, list):
                unique_data = helper.remove_duplicate_strings_from_list(str_lst=data, fuzzy=fuzzy,
                                                                        fuzzy_threshold=fuzzy_threshold)
            else:
                unique_data = data
        except Exception as e:
            gv.logger.error(e)
        return unique_data

    @staticmethod
    def filter_news(data, threshold=10, col_key="articleBody"):
        filter = False
        try:
            if data is not None:
                if len(data[col_key]) < threshold:
                    filter = True
            else:
                filter = True
        except Exception as e:
            gv.logger.error(e)
        return filter

    @staticmethod
    def filter_image_by_url(img_url):
        filter = True
        try:
            img = retrieve_image_by_url(img_url)
            if img is not None:
                filter_size = filter_by_size(img)
                filter_ar = filter_by_aspect_ratio(img)
                if filter_size or filter_ar:
                    filter = True
                else:
                    filter = False
        except Exception as e:
            pass
        return filter

    def apply_preprocessing(self, data: dict, manual_annot=False):
        output: PreprocessingOutputDocument = PreprocessingOutputDocument(message=gv.http_response_500,
                                                                          status=500)
        try:
            # Check input structure
            if isinstance(data, dict):

                if "data" in data.keys():
                    data: dict = data["data"]

                features = self.required_cols(manual_annot=manual_annot)
                # All the required features are available
                if set(list(data.keys())).issuperset(features):
                    # 2) Detect language and init NER
                    lang = self.detect_language(data=data, key="text")
                    if lang is None:
                        lang = self.detect_language(data=data, key="title")
                    data["language"] = lang

                    self.init_ner_models(lang_model=data["language"])

                    # 3) Cleaning authors
                    cleaned_authors = [self.preprocess_author_name(
                        author_name=i,
                        ner_library=self.ner_library,
                        ner_model=self.ner_model) for i in data["authors"]]
                    data["authors"] = self.get_unique_values(data=cleaned_authors, fuzzy=True,
                                                             fuzzy_threshold=80)
                    # 4) Retrieving publisher name
                    if self.websites_list is None:
                        self.websites_list = pd.read_csv(self.csv_filepath, index_col=0)

                    publisher_info = self.extract_publisher_information(source_domain=data["source_domain"],
                                                                        list_of_websites=self.websites_list,
                                                                        threshold=82)

                    data["publisher"] = publisher_info.get("name", data["source_domain"])
                    data["country"] = publisher_info.get("country", "N/A")
                    data["nationality"] = publisher_info.get("nationality", "N/A")

                    # Filter images by url
                    if not manual_annot:
                        data["images"] = self.remove_banner_images(images=data["images"])

                    status: int = 200
                    message: str = gv.http_response_200
                else:
                    status: int = 422
                    message: str = gv.http_response_422
                    data: dict = {}
            else:
                status: int = 400
                message: str = gv.http_response_400
                data: dict = {}

            # Generate output
            output: PreprocessingOutputDocument = PreprocessingOutputDocument(message=message,
                                                                              status=status,
                                                                              data=data)
        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def required_cols(manual_annot=False):
        features = {}
        try:
            if not manual_annot:
                features = {"authors", "date_created", "date_modified", "date_published", "description","identifier",
                            "images", "keywords", "language", "publish_date_estimated", "source_domain", "summary",
                            "text", "texthash", "title", "top_image", "url", "videos", "keywords"}
            else:
                features = {"authors", "title", "text", "url"}
        except Exception as e:
            gv.logger.error(e)
        return features