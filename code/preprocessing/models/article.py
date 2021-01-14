from helper import global_variables as gv


class Article:
    def __init__(self, data: dict):

        # Main fields
        self.identifier = data["identifier"]
        self.headline = data["title"]
        self.articleBody = data['text']
        self.url = data['url']
        self.sourceDomain = data['source_domain']
        self.authors: list = data['authors']
        self.language: str = data["language"]
        self.keywords: list = data.get("keywords", [])

        if "date_created" in data.keys():
            self.dateCreated = data['date_created']
        else:
            self.dateCreated = ""
        if "date_modified" in data.keys():
            self.dateModified = data['date_modified']
        else:
            self.dateModified = ""
        if "date_published" in data.keys():
            self.datePublished = data['date_published']
        else:
            self.datePublished = ""
        if "publish_date_estimated" in data.keys():
            self.publish_date_estimated = data['publish_date_estimated']
        else:
            self.publish_date_estimated = ""

        if not isinstance(data['publisher'], list):
            self.publisher = [data['publisher']]
        else:
            self.publisher = data['publisher']

        if "summary" in data.keys():
            self.summary = data['summary']
        else:
            self.summary = ""
        if "images" in data.keys():
            self.images = data['images']
        else:
            self.images = []
        if "videos" in data.keys():
            self.videos = data['videos']
        else:
            self.videos = []
        if "country" in data.keys():
            self.country = data['country']
        else:
            self.country = gv.org_default_field

        if "nationality" in data.keys():
            self.nationality = data['nationality']
        else:
            self.nationality = gv.org_default_field

        # Non-required parameters
        if 'calculatedRating' in list(data.keys()):
            self.calculatedRating = data['calculatedRating']
        else:
            self.calculatedRating = -99

        if 'calculatedRatingDetail' in list(data.keys()):
            self.calculatedRatingDetail = data['calculatedRatingDetail']
        else:
            self.calculatedRatingDetail = ""

    def article_to_dict(self):
        return self.build_kafka_output()

    def build_kafka_output(self):
        output = {}
        try:
            output = {"identifier": self.identifier, "headline": self.headline,
                      "articleBody": self.articleBody, 'url': self.url,
                      "language": self.language, "images": self.images,
                      "keywords": self.keywords, "videos": self.videos,
                      "dateCreated": self.dateCreated,
                      "dateModified": self.dateModified, "datePublished": self.datePublished,
                      "publishDateEstimated": self.publish_date_estimated, "authors": self.authors,
                      "publisher": self.publisher, "sourceDomain": self.sourceDomain, "country": self.country,
                      "nationality": self.nationality, "calculatedRating": self.calculatedRating,
                      "calculatedRatingDetail": self.calculatedRatingDetail}

        except Exception as e:
            gv.logger.error(e)
        return output