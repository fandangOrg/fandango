from helper import config as cfg


class Article:
    def __init__(self, data):

        # Main fields
        self.identifier = data["identifier"]
        self.headline = data["title"]
        self.articleBody = data['text']
        self.url = data['url']
        self.sourceDomain = data['source_domain']
        self.authors = data['authors']
        self.language = data["language"]

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
            self.country = cfg.org_default_field
        if "nationality" in data.keys():
            self.nationality = data['nationality']
        else:
            self.nationality = data["nationality"]

        # Non-required parameters
        if 'calculateRating' in list(data.keys()):
            self.calculateRating = data['calculateRating']
        else:
            self.calculateRating = -99

        if 'calculateRatingDetail' in list(data.keys()):
            self.calculateRatingDetail = data['calculateRatingDetail']
        else:
            self.calculateRatingDetail = ""

    def article_to_dict(self):
        return self.build_kafka_output()

    def build_kafka_output(self):
        output = {}
        try:
            output = {"identifier": self.identifier, "headline": self.headline,
                      "articleBody": self.articleBody, 'url': self.url,
                      "language": self.language, "images": self.images,
                      "videos": self.videos, "dateCreated": self.dateCreated,
                      "dateModified": self.dateModified, "datePublished": self.datePublished,
                      "publishDateEstimated": self.publish_date_estimated, "author": self.authors,
                      "publisher": self.publisher, "sourceDomain": self.sourceDomain, "country": self.country,
                      "nationality": self.nationality, "calculateRating": self.calculateRating,
                      "calculateRatingDetail": self.calculateRatingDetail}

        except Exception as e:
            cfg.logger.error(e)
        return output