import json
from helper import global_variables as gv


# ======================================================================================================================
# ---------------------------------------------- ARTICLE MODEL ---------------------------------------------------------
# ======================================================================================================================

class Article:
    def __init__(self, df):
        self.convert_df_to_dict(df)
        self.identifier = self.df['identifier'][0]
        self.headline = self.df['title'][0]
        self.articleBody = self.df['text'][0]
        self.url = df['url'][0]
        self.sourceDomain = self.df['source_domain'][0]

        # check if is instance of a list
        if isinstance(self.sourceDomain, list):
            self.sourceDomain = self.sourceDomain[0]

        self.language = self.df["language"][0]
        self.dateCreated = self.df['date_created'][0]
        self.dateModified = self.df['date_modified'][0]
        self.datePublished = self.df['date_published'][0]
        self.publish_date_estimated = self.df['publish_date_estimated'][0]
        self.authors = self.df['authors'][0]
        if len(self.authors) == 0:
            self.authors = [gv.default_field]
        if not isinstance(self.df['organization'][0], list):
            self.publisher = [self.df['organization'][0]]
        else:
            self.publisher = self.df['organization'][0]
        if 'calculateRating' in list(self.df.keys()):
            self.calculateRating = self.df['calculateRating'][0]
        else:
            self.calculateRating = -99
        if 'calculateRatingDetail' in list(self.df.keys()):
            self.calculateRatingDetail = self.df['calculateRatingDetail'][0]
        else:
            self.calculateRatingDetail = ""
        if 'about' in list(self.df.keys()):
            self.about = df['about'][0]
        else:
            self.about = []
        if 'mentions' in list(self.df.keys()):
            self.mentions = df['mentions'][0]
        else:
            self.mentions = []
        if 'contains' in list(self.df.keys()):
            self.contains = df['contains'][0]
        else:
            self.contains = []

        self.country = df['country'][0]
        self.nationality = df['org_nationality'][0]
        self.summary = self.df['summary'][0]
        self.images = self.df['images'][0]
        self.videos = self.df['videos'][0]
        # ------------- linkNumber -------------
        if 'linkNumber' in list(self.df.keys()):
            self.linkNumber = int(df['linkNumber'][0])
        else:
            self.linkNumber = 0

        if 'version' in list(self.df.keys()):
            self.version = df['version'][0]
        else:
            self.version = 0
        # ------------------------------------------------------------------------
        if 'fakeness' in list(self.df.keys()):
            self.fakeness = self.df['fakeness'][0]
        else:
            self.fakeness = gv.default_field
        # ------------------------------------------------------------------------

    def convert_df_to_dict(self, df):
        if not isinstance(df, dict):
            self.df = df.to_dict()

    def to_json_ES(self):
        return json.dumps(self)

    def to_dict_KAFKA(self):
        try:
            output = {"identifier": self.identifier, "headline": self.headline,
                      "articleBody": self.articleBody, 'url' : self.url,
                      "language":self.language,
                      "images": self.images, "videos": self.videos,
                      "dateCreated": self.dateCreated, "dateModified": self.dateModified,
                      "datePublished": self.datePublished, "publishDateEstimated": self.publish_date_estimated,
                      "author": self.authors, "publisher": self.publisher,
                      "sourceDomain": self.sourceDomain, "country": self.country,
                      "nationality": self.nationality, "calculateRating": self.calculateRating,
                      "calculateRatingDetail": self.calculateRatingDetail}
            # Add Fakeness whether it is available
            if self.fakeness != gv.default_field:
                output['fakeness'] = self.fakeness
        except Exception as e:
            msg = str(e) + ' Empty Document!'
            gv.logger.warning(msg)
            output = {}
        return output