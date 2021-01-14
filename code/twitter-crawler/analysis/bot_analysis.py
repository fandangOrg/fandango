import os
from helper.settings import logger
from botometer import Botometer
from data_models.api_models import BotometerAnalysisOutput


class BotAnalysisAPI(object):
    def __init__(self, consumer_key: str = None, consumer_secret: str = None,
                 access_token: str = None, access_token_secret: str = None,
                 api_key: str = None):
        self.consumer_key: str = consumer_key if consumer_key is not None else\
            os.getenv('TW_CONSUMER_KEY')
        self.consumer_secret: str = consumer_secret if consumer_secret is not None else\
            os.getenv('TW_CONSUMER_SECRET')
        self.access_token: str = access_token if access_token is not None else\
            os.getenv('TW_ACCESS_TOKEN')
        self.access_token_secret: str = access_token_secret if access_token_secret is not None else\
            os.getenv('TW_ACCESS_TOKEN_SECRET')
        self.api_key: str = api_key if api_key is not None else\
            os.getenv('BOTOMETER_API_KEY')
        self.twitter_app_auth: dict = self.set_up_twitter_auth()
        self.botometer_api: Botometer = self.set_up_botometer()

    def set_up_twitter_auth(self) -> dict:
        twitter_app_auth: dict = {}
        try:
            twitter_app_auth: dict = {
                'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'access_token': self.access_token,
                'access_token_secret': self.access_token_secret
            }
        except Exception as e:
            logger.error(e)
        return twitter_app_auth

    def set_up_botometer(self) -> Botometer:
        botometer_api: Botometer = object.__new__(Botometer)
        try:
            botometer_api: Botometer = Botometer(
                wait_on_ratelimit=True,
                rapidapi_key=self.api_key,
                **self.twitter_app_auth)

        except Exception as e:
            logger.error(e)
        return botometer_api

    def analyse_account_by_id(self, user_id: int) -> BotometerAnalysisOutput:
        output: BotometerAnalysisOutput = BotometerAnalysisOutput()
        try:
            # Check a single account by id
            response: dict = self.botometer_api.check_account(user_id)
            if response.get("cap", False):
                output: BotometerAnalysisOutput = BotometerAnalysisOutput(
                    cap=response.get("cap", {}),
                    display_scores=response.get("display_scores", {}),
                    analysed=True)
        except Exception as e:
            logger.warning(e)
        return output

