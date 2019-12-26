
# ======================================================================================================================
# ----------------------------------------------- AUTHOR MODEL ---------------------------------------------------------
# ======================================================================================================================
import json


class Author:
    def __init__(self,identifier="", name="", url="", nationality="", bias="", jobTitle="",
                 gender="",affiliation="", trustworthiness=-99):
        self.identifier = identifier
        self.name = name
        self.url = url
        self.nationality = nationality
        self.bias = bias
        self.jobTitle = jobTitle
        self.gender=gender
        self.affiliation = affiliation
        self.trustworthiness = trustworthiness
        
    def to_json(self, id=False):
        if id:
            response = {"identifier": self.identifier, "name": self.name, "url": self.url, "nationality": self.nationality,
                        "bias": self.bias, "jobTitle": self.jobTitle, "gender": self.gender,
                        "affiliation": self.affiliation, "trustworthiness": self.trustworthiness}
        else:
            response = {"name": self.name, "url": self.url, "nationality": self.nationality,
                        "bias": self.bias, "jobTitle": self.jobTitle, "gender": self.gender,
                        "affiliation": self.affiliation, "trustworthiness": self.trustworthiness}
        return json.dumps(response)

    def to_dict(self, id=False):
        if id:
            response = {"identifier": self.identifier, "name": self.name, "url": self.url, "nationality": self.nationality,
                        "bias": self.bias, "jobTitle": self.jobTitle, "gender": self.gender,
                        "affiliation": self.affiliation, "trustworthiness": self.trustworthiness}
        else:
            response = {"name": self.name, "url": self.url, "nationality": self.nationality,
                        "bias": self.bias, "jobTitle": self.jobTitle, "gender": self.gender,
                        "affiliation": self.affiliation, "trustworthiness": self.trustworthiness}
        return response

    @classmethod
    def from_dict(cls, author, identifier):
        return cls(identifier, author["name"], author["url"], author["nationality"],
                   author["bias"], author["jobTitle"], author["gender"],
                   author["affiliation"], author["trustworthiness"])