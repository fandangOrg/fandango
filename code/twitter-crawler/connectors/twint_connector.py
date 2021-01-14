from twint import Config
from helper.settings import logger


class TwintConnector(object):
    def __init__(self):
        self.config: Config = Config()

    def set_up_configuration(self, query: str, year: int, since: str, until: str, language: str):
        try:
            self.config.Search: str = query
            self.config.Year: int = year
            self.config.Since: str = since
            self.config.Until: str = until
            self.config.Lang: str = language
        except Exception as e:
            logger.error(e)

