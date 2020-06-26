from helper import global_variables as gv


class Article:
    def __init__(self, identifier=None, headline=None, articleBody=None, url=None, source_domain=None,
                 language=None, date_created=None, date_modified=None, date_published=None,
                 publish_date_estimated=None, authors=None, publisher=None, summary=None, images=None,
                 videos=None, country=None, nationality=None, calculate_rating=None,
                 calculate_rating_detail=None, fakeness=None):

        # Main fields
        self.identifier = identifier
        self.headline = headline
        self.articleBody = articleBody
        self.url = url
        self.sourceDomain = source_domain

        self.language = language
        self.dateCreated = date_created
        self.dateModified = date_modified
        self.datePublished = date_published
        self.publishDateEstimated = publish_date_estimated
        self.authors = authors

        # TODO: Remove list from publisher
        if not isinstance(publisher, list):
            self.publisher = publisher
        else:
            self.publisher = publisher

        self.summary = summary
        self.images = images
        self.videos = videos
        self.country = country
        self.nationality = nationality
        self.calculatedRating = calculate_rating
        self.calculatedRatingDetail = calculate_rating_detail
        self.fakeness = fakeness

    def article_from_dict(self, data):
        # Main fields
        self.identifier = data["identifier"]
        self.headline = data["headline"]
        self.articleBody = data['articleBody']
        self.url = data['url']
        self.sourceDomain = data['sourceDomain']

        self.language = data["language"]
        self.dateCreated = data['dateCreated']
        self.dateModified = data['dateModified']
        self.datePublished = data['datePublished']
        self.publishDateEstimated = data['publishDateEstimated']
        self.authors = data['author']

        # TODO: Remove list from publisher
        if not isinstance(data['publisher'], list):
            self.publisher = [data['publisher']]
        else:
            self.publisher = data['publisher']

        self.images = data['images']
        self.videos = data['videos']
        self.country = data['country']
        self.nationality = data['nationality']

        # Non-required parameters

        if "summary" in list(data.keys()):
            self.summary = data['summary']
        else:
            self.summary = ""

        if 'calculatedRating' in list(data.keys()):
            self.calculatedRating = data['calculatedRating']
        else:
            self.calculatedRating = -99

        if 'calculatedRatingDetail' in list(data.keys()):
            self.calculatedRatingDetail = data['calculatedRatingDetail']
        else:
            self.calculatedRatingDetail = ""

        # TODO: Review parameter
        if 'fakeness' in list(data.keys()):
            self.fakeness = data['fakeness']
        else:
            self.fakeness = gv.default_field

        art = Article(identifier=self.identifier, headline=self.headline, articleBody=self.articleBody, url=self.url,
                      source_domain=self.sourceDomain, language=self.language, date_created=self.dateCreated,
                      date_modified=self.dateModified, date_published=self.datePublished,
                      publish_date_estimated=self.publishDateEstimated, authors=self.authors, publisher=self.publisher,
                      summary=self.summary, images=self.images, videos=self.videos, country=self.country,
                      nationality=self.nationality, calculate_rating=self.calculatedRating,
                      calculate_rating_detail=self.calculatedRatingDetail, fakeness=self.fakeness)

        return art

    def article_to_dict(self):
        return self.build_output()

    def build_output(self):
        output = {}
        try:
            output = {"identifier": self.identifier, "headline": self.headline,
                      "articleBody": self.articleBody, 'url': self.url,
                      "language": self.language, "images": self.images,
                      "videos": self.videos, "dateCreated": self.dateCreated,
                      "dateModified": self.dateModified, "datePublished": self.datePublished,
                      "publishDateEstimated": self.publishDateEstimated, "author": self.authors,
                      "publisher": self.publisher, "sourceDomain": self.sourceDomain, "country": self.country,
                      "nationality": self.nationality, "calculatedRating": self.calculatedRating,
                      "calculatedRatingDetail": self.calculatedRatingDetail}

            # Add Fakeness whether it is available
            if self.fakeness != gv.default_field and self.fakeness is not None:
                output['fakeness'] = self.fakeness
        except Exception as e:
            gv.logger.error(e)
        return output

    @staticmethod
    def get_required_properties():
        properties = ["identifier", "headline", "articleBody", 'url', "language",
                      "images", "videos", "dateCreated", "dateModified", "datePublished",
                      "publishDateEstimated", "author", "publisher", "sourceDomain", "country",
                      "nationality", "calculatedRating", "calculatedRatingDetail"]
        return properties