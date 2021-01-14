from data_models.twitter_models import TwitterDocument
from tweepy.models import User, Status
from helper.utils import (preprocess_date, get_average_tweets_per_day,
                          get_account_age_in_days)
from langdetect import detect


class FANDANGOUserAccountDoc(TwitterDocument):
    def __init__(self, user: User):
        self.created_at: str = preprocess_date(user.__getattribute__(
            "created_at"))
        self.default_profile: bool = user.__getattribute__(
            "default_profile")
        self.default_profile_image: bool = user.__getattribute__(
            "default_profile_image")
        self.favourites_count: int = user.__getattribute__(
            "favourites_count")
        self.followers_count: int = user.__getattribute__(
            "followers_count")
        self.friends_count: int = user.__getattribute__(
            "friends_count")
        self.geo_enabled: bool = user.__getattribute__(
            "geo_enabled")
        self.id: int = user.__getattribute__("id")
        self.lang: str = self.get_language(text=user.__getattribute__("description"))
        self.location: str = "N/A" if user.__getattribute__(
            "location") is None or user.__getattribute__(
            "location") == "" else user.__getattribute__("location")
        self.statuses_count: int = user.__getattribute__(
            "statuses_count")
        self.profile_background_image_url: str = user.__getattribute__(
            "profile_background_image_url")
        self.profile_image_url: str = user.__getattribute__(
            "profile_image_url")
        self.screen_name: str = user.__getattribute__(
            "screen_name")
        self.verified: bool = user.__getattribute__(
            "verified")
        self.average_tweets_per_day: float = get_average_tweets_per_day(
            statuses_count=self.statuses_count, created_at=user.__getattribute__(
                "created_at"))
        self.account_age_days: int = get_account_age_in_days(
            created_at=user.__getattribute__("created_at"))
        self.botometer_analysis: dict = {}
        self.uuid: str = self.get_128_uuid(data_str=str(self.id))
        # TODO: Profile image + url of the tweet + screen_name


class FANDANGOStatusDoc(TwitterDocument):
    def __init__(self, status: Status):
        self.created_at: str = preprocess_date(status.__getattribute__(
            "created_at"))
        self.id: int = status.__getattribute__("id")
        self.hashtags: list = status.__getattribute__("entities").get("hashtags", [])
        self.user_mentions: list = status.__getattribute__("entities").get("user_mentions", [])
        # self.urls: list = status.__getattribute__("entities").get("urls", [])
        # self.media: list = status.__getattribute__("entities").get("media", [])
        self.text: str = self.get_text(status=status)
        self.retweet_count: int = status.__getattribute__("retweet_count")
        self.retweeted: bool = status.__getattribute__("retweeted")
        self.user_id: int = status.__getattribute__("user").__getattribute__("id")
        self.profile_image_url: str = status.__getattribute__("user").__getattribute__(
            "profile_image_url")
        self.screen_name: str = status.__getattribute__("user").__getattribute__(
            "screen_name")
        self.possibly_sensitive: bool = status.__getattribute__("possibly_sensitive") if \
            hasattr(status, 'possibly_sensitive') else False
        self.favorite_count: int = status.__getattribute__("favorite_count")
        self.favorited: bool = status.__getattribute__("favorited")
        self.lang: str = detect(self.text)
        self.sentiment_analysis: dict = {}
        self.source: str = status.__getattribute__("source")
        self.geolocation: str = self.get_geolocation(status=status)
        self.place: dict = self.get_place(status=status)
        self.url: str = f"https://twitter.com/user/status/{status.__getattribute__('id')}"
        self.uuid: str = self.get_128_uuid(data_str=str(self.id))
        self.user_uuid: str = self.get_128_uuid(data_str=str(self.user_id))

    @staticmethod
    def get_place(status: Status) -> dict:
        place: dict = {"coordinates": [], "country": "N/A",
                       "country_code": "N/A", "full_name": "N/A"}
        try:
            if status.__getattribute__("place") is not None:
                status_place: dict = status.__getattribute__("place").__dict__
                coordinates: list = status_place.get("bounding_box").__dict__.get(
                    "coordinates", [])
                country: str = status_place.get("country", "N/A")
                country_code: str = status_place.get("country_code", "N/A")
                full_name: str = status_place.get("full_name", "N/A")
                place: dict = {"coordinates": coordinates, "country": country,
                               "country_code": country_code, "full_name": full_name}
        except Exception as e:
            pass
        return place

    @staticmethod
    def get_geolocation(status: Status) -> str:
        geolocation: str = "0,0"
        try:
            coordinates: dict = status.__getattribute__("coordinates") if \
                hasattr(status, 'coordinates') else {}
            if coordinates:
                geolocation: str = f"{coordinates.get('coordinates', '')[1]}," \
                    f" {coordinates.get('coordinates', '')[0]}"
        except Exception as e:
            pass
        return geolocation


    @staticmethod
    def get_text(status: Status) -> str:
        if hasattr(status, "full_text"):  # Check if Retweet
            try:
                text: str = status.__getattribute__("full_text")
            except AttributeError:
                text: str = status.__getattribute__("text")
        else:
            try:
                text: str = status.__getattribute__("extended_tweet").__getattribute__("full_text")
            except AttributeError:
                text: str = status.__getattribute__("text")
        return text