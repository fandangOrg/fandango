from langdetect import detect
import pandas as pd
import numpy as np
import os
import spacy
import tldextract
import re
import string
import unidecode
from restcountries import RestCountryApiV2 as rapi
from difflib import SequenceMatcher
from helper.helper import (domain_stop_words,
                           check_organization_data,
                           get_fake_media, check_authorname_org,
                           get_stop_words)

from helper import global_variables as gv


class FandangoPreprocesing():
    def __init__(self, raw_art, newspapers_list, drop_cols=None,
                 lang_model='xx'):
        self.raw_art = raw_art
        self.rename_columns()
        self.drop_cols=drop_cols
        #self.remove_empty_text_title()
        self.remove_selected_columns()
        self.fake_media = get_fake_media()
        self.newspapers_list = newspapers_list + self.fake_media
        self.domain_stopWords = domain_stop_words()
        self.author_stopWords = get_stop_words()
        self.preprocessed_data = None
        self.df_all_items = None
        self.lang_model = lang_model
        self.spacy_model = self.select_spacy_model()
        self.nlp = spacy.load(self.spacy_model)
        self.total_cleaned_data = None
    
    def select_spacy_model(self):
        model_name = ''
        try:
            if self.lang_model=='en':
                model_name = 'en_core_web_sm'
            elif self.lang_model =='it':
                model_name = 'it_core_news_sm'
            elif self.lang_model =='de':
                model_name = 'de_core_news_sm'
            elif self.lang_model =='es':
                model_name = 'es_core_news_sm'
            elif self.lang_model =='nl':
                model_name= 'nl_core_news_sm'
            elif self.lang_model =='xx':
                model_name = 'xx_ent_wiki_sm'
        except Exception as e:
            gv.logger.error(e)
        return model_name
    
    def remove_selected_columns(self):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        # OUTPUT:
        #       - ok: boolean indicator of the process.
        # ================================================= 
        ok=True
        try:
            df_temp_art = self.raw_art.copy()
            
            if self.drop_cols is not None:
                for col in self.drop_cols:
                    if col in list(self.raw_art.columns):
                        df_temp_art.drop(col, axis=1, inplace=True)
            # Update DataFrame
            self.raw_art = df_temp_art.copy()
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok
    
    def remove_empty_text_title(self):
        ok=False
        try:
            self.raw_art = self.raw_art[self.raw_art.text !='']
            self.raw_art = self.raw_art[self.raw_art.title !='']
            ok=True
        except Exception as e:
            gv.logger.error(e)
        return ok
    
    def rename_columns(self):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        # OUTPUT:
        #       - ok: boolean indicator of the process.
        # =================================================        
        ok=True
        try:
            rename_cols = ['date_publish', 'date_modify', 'date_download']
            new_cols = ['date_published', 'date_modified', 'date_created']
            for i, col in enumerate(rename_cols):
                if self.raw_art is not None and col in list(self.raw_art.columns):
                    self.raw_art = self.raw_art.rename(columns={col: new_cols[i]})
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok

    def replace_empty_list(self, df):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - df: Pandas DataFrame.
        # OUTPUT:
        #       - df: Pandas DataFrame.
        # =================================================
        
        df = df.mask(df.applymap(str).eq('[]'))
        df.fillna(value=pd.np.nan, inplace=True)
        return df

    def detect_language(self, row):
        # ================================================
        # INPUT:
        #       - self: Pre-process object.
        #       - row: Pandas DataFrame Row
        # OUTPUT:
        #       - lang: Language code detected
        # =================================================
        text = str(row['text'])
        title = str(row['title'])
        lang = str(row['language'])
        try:
            if len(text)>5 and text != '':
                lang = detect(text)
            elif len(title)>5 and title !='':
                lang = detect(title)
        except Exception as e:
            gv.logger.error(e)
        return lang
    
    def remove_lineBreaks(self, row, col):
        text = str(row[col])
        try:
            text = text.replace("\r","").replace("\n","")
        except Exception as e:
            gv.logger.error(e)
        return text
    
    def clean_authorName(self, row):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - row: List of authors.
        # OUTPUT:
        #       - row: list of the cleaned names.
        # ================================================

        source_domain = row['source_domain']
        list_domains = tldextract.extract(source_domain)
        domain = list_domains.domain

        old_authors = row['authors']
        new_authors = []
        if old_authors is not None and old_authors is not np.nan and len(old_authors)>0:
            for i, authorName in enumerate(old_authors):
                authorName = authorName.replace('  ', ' ')
                # a) Regular expression
                author_data_ls = re.split(r'(\(|\))|\&|(\[|\])|\/|\| and | for |  +',authorName.lower())
                found=False
                for aut in author_data_ls:
                    # Empty
                    if aut is not None and len(aut.strip())>1 :
                        if not found:
                            authorName=aut.strip()
                            found=True
                        else:
                            if aut.strip() not in old_authors:
                                old_authors.append(aut.strip())

                # ---------------------------------------------------------------------------------
                # Remove numbers and puctuation
                authorName = re.sub('[0-9]+', '', authorName)
                authorName = authorName.rstrip(string.punctuation)
                is_org = check_authorname_org(authorName=authorName, organizations_list=self.newspapers_list)

                if len(authorName)>3 and not is_org  and "@" not in authorName:
                    for word in self.author_stopWords:
                        authorName = authorName.lower().replace(word.lower(), '')
                    authorName = authorName.strip()
                    authorName = authorName.replace("\n","")
                    authorName = (unidecode.unidecode(authorName))
                    # 2) Named Entity Recognition Multilingual mode
                    doc = self.nlp(authorName.title())
                    # Check if the name comes from a Person
                    if len(doc.ents)>0:
                        for ent in doc.ents:
                            gv.logger.warning(ent.label_ )
                            if ent.label_ == 'PER' or ent.label_ == 'PERSON':
                                authorName = str(ent)
                                if new_authors:
                                    insert=True
                                    for j, next_aut in enumerate(new_authors):
                                        dist = SequenceMatcher(None, authorName, next_aut).ratio()
                                        # It is the same
                                        if dist >= 0.7:
                                            if(len(authorName)<len(next_aut)):
                                                new_authors[j]=authorName
                                            insert=False
                                    if insert:
                                        authorName = authorName.title()
                                        new_authors.append(authorName)
                                else:
                                    authorName = authorName.title()
                                    # Add entry to the list
                                    new_authors.append(authorName)

        # -----------------------------------------------------------------
        else:
            new_authors.append(gv.default_field)

        return list(set(new_authors))


    def extract_organization(self, row):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - row: the source domain.
        # OUTPUT:
        #       - row: cleaned_org: detected Organization.
        # ================================================

        organization = row
        # Obtain Organization data
        org_data = check_organization_data(organization, self.newspapers_list, threshold=90)
        return org_data

    def preprocess_text_title(self, text_col=['title', 'text', 'summary']):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - fake: boolean indicating the 
        # OUTPUT:
        #       - lang: Language code detected
        # =================================================
        ok = True
        try:
            for col in text_col:
                if col in list(self.preprocessed_data.columns):
                    new_col = col + '_cleaned'
                    self.preprocessed_data[new_col] = self.preprocessed_data.apply(lambda x: self.remove_lineBreaks(x, col),axis=1)
                    self.preprocessed_data.drop(col, axis=1, inplace=True)
                    self.preprocessed_data = self.preprocessed_data.rename(columns={new_col: col})
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok


    def preprocess_language(self, lang_col='language'):
        ok=True
        try:
            if lang_col in list(self.preprocessed_data.columns):
                # preprocessed DataFrame
                self.preprocessed_data['text'] = self.preprocessed_data['text'].apply(str)
                self.preprocessed_data['title'] = self.preprocessed_data['title'].apply(str)
                self.preprocessed_data['language'] = self.preprocessed_data['language'].apply(str)
                self.preprocessed_data['language_cl'] = self.preprocessed_data.apply(self.detect_language,axis=1)
                
                # Remove original author columns
                self.preprocessed_data.drop(lang_col, axis=1, inplace=True)
                # Rename Column
                self.preprocessed_data = self.preprocessed_data.rename(columns={'language_cl': lang_col})
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok


    def preprocess_authors(self, author_col='authors'):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - fake: Boolean indicating the fakeness of the data
        #       - author_col: author column of the DataFrame
        # OUTPUT:
        #       - ok: True if the process was fine, False if not.
        # ================================================
        
        ok=True
        df = self.raw_art.copy()
        try:
            if df is not None:

                # Clean Author
                df.fillna(value=np.nan, inplace=True) 
                # preprocessed DataFrame
                self.preprocessed_data = df.copy()
                self.preprocessed_data['authors_cl']  = self.preprocessed_data.apply(self.clean_authorName,axis=1)
                self.preprocessed_data['authors_cl'] =  self.preprocessed_data['authors_cl'].apply(lambda y: [gv.default_field] if len(y) == 0 else y)

                # Remove original author columns
                self.preprocessed_data.drop(author_col, axis=1, inplace=True)
                # Rename Column
                self.preprocessed_data = self.preprocessed_data.rename(columns={'authors_cl': author_col})

        except Exception as e:
            ok = False
            gv.logger.error(e)
        return ok


    def extract_domain(self, row):
        source_domain = ''
        try:
            url = row['source_domain']
            list_domain = tldextract.extract(url)
            source_domain = list_domain.fqdn
        except Exception as e:
            gv.logger.error(e)
        return source_domain


    def preprocess_organization(self):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - fake: Boolean indicating the fakeness of the data
        # OUTPUT:
        #       - ok: True if the process was fine, False if not.
        # ================================================
        
        ok=True
        try:
            # Create an Organization
            org_data = self.extract_organization(row=self.preprocessed_data['source_domain'].values[0])
            self.preprocessed_data['organization'] = org_data['name']
            self.preprocessed_data['country'] = org_data['country']
            if org_data['country'] != 'Not Specified':
                self.preprocessed_data['org_nationality'] = rapi.get_countries_by_name(org_data['country'])[0].demonym
            else:
                self.preprocessed_data['org_nationality'] = 'Not Specified'

            if 'fakeness' in list(self.raw_art.columns):
                self.preprocessed_data['bias'] = self.preprocessed_data['fakeness'].values[0]
            else:
                self.preprocessed_data['bias'] = gv.default_field
            self.preprocessed_data['parent_org'] = org_data['parent_org']
            self.preprocessed_data['source_domain'] = self.preprocessed_data.apply(self.extract_domain, axis=1)

        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok


    def preprocess_entities_topics(self):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - fake: Boolean indicating the fakeness of the data
        # OUTPUT:
        #       - ok: True if the process was fine, False if not.
        # ================================================
        
        ok=True
        try:
            # Change the dataset of newspapers in the fake case
            # Create an Organization
            self.preprocessed_data['entities'],  self.preprocessed_data['topics'] = zip(*self.preprocessed_data['text'].apply(
                self.extract_entities_topics))
        except Exception as e:
            gv.logger.error(e)
            ok=False
        return ok


    def check_dates(self, colname):
        try:

            # publish date estimated
            if self.total_cleaned_data['publish_date_estimated'].values[0] == 'yes':
                pass
            else:
                self.total_cleaned_data[colname] = self.total_cleaned_data['date_created'].values[0]

            """# Convert to string
            if isinstance(self.total_cleaned_data['publish_date_estimated'].values[0], bool):
                self.total_cleaned_data['publish_date_estimated'] = str(self.total_cleaned_data['publish_date_estimated'].values[0])
            # False
            elif not ast.literal_eval(self.total_cleaned_data['publish_date_estimated'].values[0]):
                self.total_cleaned_data[colname] = self.total_cleaned_data['date_created'].values[0]
            else:
                pass"""

        except Exception as e:
            gv.logger.error(e)


    def extract_entities_topics(self, row):
        entities = []
        topics = []
        try:
            doc = self.nlp(row)
            entities = []
            topics = []
            
            if len(doc) > 1:
                for e in doc.ents:
                    # Topics
                    if e.label_=='EVENT' or e.label_=='LOC' or e.label_=='PRODUCT' or e.label_== 'MISC':
                        topics.append(e.text)
                    # Entities
                    if e.label_== 'PER' or e.label_ == 'PERSON' or e.label_ == 'ORG' or e.label_=='FAC' or e.label_=='NORP' or e.label_=='GPE' or e.label_=='WORK_OF_ART':
                        entities.append(e.text)
        except Exception as e:
            gv.logger.error(e)
        return entities, topics

    def run(self, save_local=False,
            filename='preprocessed_data.csv', filedir='data'):
        # ================================================
        # INPUT:
        #       - self: Preprocess object.
        #       - save_local: Save the data locally in a csv file
        #       - together: boolean indicating if there are two 
        #                   different indexes
        #       - filename: name of the csv file 
        #       - filedir: name of the directory
        # OUTPUT:
        #      - ok: True if the process was fine, False if not.
        # ================================================ 
        
        ok=False
        try:
            if (self.raw_art is not None and not self.raw_art.empty and self.raw_art['text'].values[0] is not None and
                    len(self.raw_art['text'].values[0]) > 5):
                # Articles
                gv.logger.info('Cleaning Authors!')
                self.preprocess_authors()
                gv.logger.info('Cleaning Organizations!')
                self.preprocess_organization()

                gv.logger.info('Analyzing the language!')
                self.preprocess_language()
                gv.logger.info('Analyzing article content!')
                self.preprocess_text_title()

                # Add identifier to the article using Texthash
                self.total_cleaned_data = self.preprocessed_data.copy()

                # Replace Nans and remove duplicates articles using ID
                self.total_cleaned_data.replace(to_replace=[None], value=np.nan, inplace=True)
                self.total_cleaned_data.fillna(value=gv.default_field, inplace=True)
                if save_local:
                    if not os.path.exists(filedir):
                        os.makedirs(filedir)
                    full_path = os.path.join(filedir, filename)
                    self.total_cleaned_data.to_csv(full_path)
                ok=True
            else:
                ok = False
        except Exception as e:
            gv.logger.error(e)
        return ok