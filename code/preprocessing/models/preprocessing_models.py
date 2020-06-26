from dotmap import DotMap
from helper import global_variables as gv


class PreprocessingDocument:
    def dict_from_class(self):
        return dict((key, value)
                    for (key, value) in self.__dict__.items())

    @staticmethod
    def dot_map_from_dict(data_dict: {dict}):
        return DotMap(data_dict)


class PreprocessingInputDocument(PreprocessingDocument):
    def __init__(self, identifier: str, title: str, text: str, url: str,
                 source_domain: str, authors: list, language: str,
                 publisher: str, date_created: str = "",
                 date_modified: str = "", date_published: str = "",
                 publish_date_estimated: str = "", summary: str = "",
                 images: list = None, videos: list = None,
                 country: str = None, nationality: str = None,
                 calculatedRating: float = -99,
                 calculatedRatingDetail: dict = None):

        self.identifier: str = identifier
        self.headline: str = title
        self.articleBody: str = text
        self.url: str = url
        self.sourceDomain: str = source_domain
        self.authors: list = authors
        self.language: str = language
        self.dateCreated: str = date_created
        self.dateModified: str = date_modified
        self.datePublished: str = date_published
        self.publish_date_estimated: str = publish_date_estimated
        self.publisher: list = [publisher] if not isinstance(publisher, list) else publisher
        self.summary: str = summary
        self.images: list = [] if images is None else images
        self.videos: list = [] if videos is None else videos
        self.country: str = gv.org_default_field if country is None else country
        self.nationality: str = gv.org_default_field if nationality is None else nationality
        self.calculatedRating: float = calculatedRating
        self.calculatedRatingDetail: dict = {} if calculatedRatingDetail is None else calculatedRatingDetail


class PreprocessingOutputDocument(PreprocessingDocument):
    def __init__(self, message: str, status: int, data: dict = None):
        self.message: str = message
        self.status: int = status
        self.data: dict = {} if data is None else data
