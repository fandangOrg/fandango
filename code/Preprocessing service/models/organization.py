import json



# ======================================================================================================================
# ------------------------------------------- ORGANIZATION MODEL -------------------------------------------------------
# ======================================================================================================================

class Organization:
    def __init__(self,identifier="", name="", url="", nationality="", country="", bias="", parentOrganization="",
                 trustworthiness=-99):
        self.identifier = identifier
        self.name = name
        if isinstance(url, list):
            self.url = url[0]
        else:
            self.url = url
        self.nationality = nationality
        self.country = country
        self.bias = bias
        self.parentOrganization = parentOrganization
        self.trustworthiness = trustworthiness

    def to_json(self, id=False):
        if id:
            response = {"identifier": self.identifier, "name": self.name, "url": self.url, "nationality": self.nationality,
                        "country":self.country, "bias": self.bias, "parentOrganization": self.parentOrganization,
                        "trustworthiness": self.trustworthiness}
        else:
            response = {"name": self.name, "url": self.url, "nationality": self.nationality,
                        "country": self.country, "bias": self.bias,
                        "parentOrganization": self.parentOrganization,
                        "trustworthiness": self.trustworthiness}
        return json.dumps(response)

    def to_dict(self, id=False):
        if id:
            response = {"identifier": self.identifier, "name": self.name, "url": self.url, "nationality": self.nationality,
                        "country":self.country, "bias": self.bias, "parentOrganization": self.parentOrganization,
                        "trustworthiness": self.trustworthiness}
        else:
            response = {"name": self.name, "url": self.url, "nationality": self.nationality,
                        "country":self.country, "bias": self.bias,
                        "parentOrganization": self.parentOrganization,
                        "trustworthiness": self.trustworthiness}
        return response

    @classmethod
    def from_dict(cls, organization, identifier):
        return cls(identifier, organization["name"], organization["url"], organization["nationality"],
                   organization['country'], organization['bias'], organization["parentOrganization"],
                   organization["trustworthiness"])