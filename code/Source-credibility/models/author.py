from helper.helper import normalize_value
from helper import global_variables as gv


class Author:
    def __init__(self, identifier=None, name=None, affiliation=None, url=None, nationality="", bias="",
                 job_title="", gender="", status="inProgress", trustworthiness=None, relevance=None):
        self.identifier = identifier
        self.name = name
        if isinstance(affiliation, list):
            self.affiliation = affiliation[0]
        else:
            self.affiliation = affiliation

        self.url = url
        self.nationality = nationality
        self.bias = bias
        self.job_title = job_title
        self.gender = gender
        self.status = status

        if trustworthiness is not None:
            self.trustworthiness = trustworthiness
        else:
            self.trustworthiness = normalize_value()

        if relevance is not None:
            self.relevance = relevance
        else:
            self.relevance = 0

    def author_to_dict(self):
        return self.build_output()

    def to_source_data_dict(self):
        return self.build_source_data()

    def build_output(self):
        output = {}
        try:
            output = {"identifier": self.identifier, "name": self.name, "url": self.url,
                      "nationality": self.nationality, "bias": self.bias, "jobTitle": self.job_title,
                      "gender": self.gender, "affiliation": self.affiliation, "status": self.status,
                      "trustworthiness": self.trustworthiness, "relevance": self.relevance}
        except Exception as e:
            gv.logger.error(e)
        return output

    def build_source_data(self):
        output = {}
        try:
            output = {"name": self.name, "url": self.url,
                      "nationality": self.nationality, "bias": self.bias, "jobTitle": self.job_title,
                      "gender": self.gender, "affiliation": self.affiliation, "status": self.status,
                      "trustworthiness": self.trustworthiness, "relevance": self.relevance}
        except Exception as e:
            gv.logger.error(e)
        return output