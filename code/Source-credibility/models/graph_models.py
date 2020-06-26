from dotmap import DotMap


class GraphAnalyzerDoc:
    def dict_from_class(self):
        return dict((key, value)
                    for (key, value) in self.__dict__.items())

    @staticmethod
    def dot_map_from_dict(data_dict: {dict}):
        return DotMap(data_dict)


class GraphAnalyzerOutputDoc(GraphAnalyzerDoc):
    def __init__(self, message: str, status: int, data: dict = None):
        self.message: str = message
        self.status: int = status
        self.data: dict = {} if data is None else data


class AnalysisDoc(GraphAnalyzerDoc):
    def __init__(self, identifier: str = "", authors: list = None, publisher: list = None):
        self.identifier: str = identifier
        self.authors: list = [] if authors is None else authors
        self.publisher: list = [] if publisher is None else publisher


class Neo4jInputDoc(GraphAnalyzerDoc):
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
