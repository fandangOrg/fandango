from helper.utils import normalize_value
from helper.settings import logger


class Publisher:
    def __init__(self, identifier=None, name=None, url=None, country=None, nationality=None, bias="",
                 parent_organization="", status="inProgress", trustworthiness=None, relevance=None):
        self.identifier = identifier
        self.name = name
        if isinstance(url, list):
            self.url = url[0]
        else:
            self.url = url

        self.country = country
        self.nationality = nationality
        self.bias = bias
        self.parent_organization = parent_organization
        self.status = status

        if trustworthiness is not None:
            self.trustworthiness = trustworthiness
        else:
            self.trustworthiness = normalize_value()

        if relevance is not None:
            self.relevance = relevance
        else:
            self.relevance = 1

    def publisher_to_dict(self):
        return self.build_output()

    def to_source_data_dict(self):
        return self.build_source_data()

    def build_output(self):
        output = {}
        try:
            output = {"identifier": self.identifier, "name": self.name, "url": self.url,
                      "nationality": self.nationality, "country": self.country, "bias": self.bias,
                      "parentOrganization": self.parent_organization, "status": self.status,
                      "trustworthiness": self.trustworthiness, "relevance": self.relevance}
        except Exception as e:
            logger.error(e)
        return output

    def build_source_data(self):
        output = {}
        try:
            output = {"name": self.name, "url": self.url,
                      "nationality": self.nationality, "country": self.country, "bias": self.bias,
                      "parentOrganization": self.parent_organization, "status": self.status,
                      "trustworthiness": self.trustworthiness, "relevance": self.relevance}
        except Exception as e:
            logger.error(e)
        return output