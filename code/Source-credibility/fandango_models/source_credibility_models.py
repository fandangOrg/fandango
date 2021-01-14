from helper.utils import preprocess_date
from datetime import datetime


class GraphAnalyzerOutputDoc(object):
    def __init__(self, message: str, status: int, data: dict = None):
        self.message: str = message
        self.status: int = status
        self.data: dict = {} if data is None else data


class AnalysisDoc(object):
    def __init__(self, identifier: str = "", authors: list = None, publisher: list = None):
        self.identifier: str = identifier
        self.authors: list = [] if authors is None else authors
        self.publisher: list = [] if publisher is None else publisher


class Neo4jInputDoc(object):
    def __init__(self, article: dict, authors: dict, publisher: dict):
        self.article: dict = article
        self.authors: dict = authors
        self.publisher: dict = publisher


class Neo4jOutputDoc(GraphAnalyzerOutputDoc):
    def __init__(self, message: str, status: int, data: dict = None):
        super().__init__(message=message, status=status, data=data)


class SourceCredibilityOutputDoc(GraphAnalyzerOutputDoc):
    def __init__(self, message: str, status: int, data: dict = None):
        super().__init__(message=message, status=status, data=data)


class TrustworthinessDoc(object):
    def __init__(self, trustworthiness: float, relevance: float,
                 analysed: bool = False, error: bool = True):
        self.trustworthiness: float = trustworthiness
        self.relevance: float = relevance
        self.analysed: bool = analysed
        self.error: bool = error


class PublisherFeaturesDoc(object):
    def __init__(self, open_rank_analysis: dict, suffix_rank_analysis: dict, whois_rank_analysis: dict,
                 category_rank_analysis: dict, twitter_rank_analysis: dict, text_rank_analysis: dict,
                 anonymous_rank_analysis: dict):
        self.open_rank_analysis: dict = open_rank_analysis
        self.suffix_rank_analysis: dict = suffix_rank_analysis
        self.whois_rank_analysis: dict = whois_rank_analysis
        self.category_rank_analysis: dict = category_rank_analysis
        self.twitter_rank_analysis: dict = twitter_rank_analysis
        self.text_rank_analysis: dict = text_rank_analysis
        self.anonymous_rank_analysis: dict = anonymous_rank_analysis
        self.last_updated: str = preprocess_date(
            non_formatted_date=datetime.utcnow())


class AuthorFeatureDoc(object):
    def __init__(self, publisher_rank_analysis: dict, text_rank_analysis: dict):
        self.publisher_rank_analysis: dict = publisher_rank_analysis
        self.text_rank_analysis: dict = text_rank_analysis
        self.last_updated: str = preprocess_date(
            non_formatted_date=datetime.utcnow())


class GeneralAPIResponse(object):
    def __init__(self, status_code: int, message: str, data: dict):
        self.status_code: int = status_code
        self.message: str = message
        self.data: dict = data
