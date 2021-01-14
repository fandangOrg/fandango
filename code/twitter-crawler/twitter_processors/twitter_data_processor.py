from tweepy import Status, User
from data_models.twitter_models import UserAccountDoc, StatusDoc, TwitterDataOutput
from data_models.api_models import (FlairSentOutput, TextBlobSentOutput,
                                    NLTKSentOutput, SentimentAnalysisOutput,
                                    BotometerAnalysisOutput)
from helper.settings import logger
from analysis.sentiment_analysis import SentimentAnalysisAPI
from analysis.bot_analysis import BotAnalysisAPI


class TwitterDataProcessor(object):
    min_char: int = 3
    @staticmethod
    def process_twitter_data(status: Status, twitter_credentials: dict,
                             add_sentiment: bool = True,
                             add_bot_analysis: bool = True) -> TwitterDataOutput:
        output: TwitterDataOutput = TwitterDataOutput(status={}, user={})
        try:

            # 1. Retrieve status document
            status_doc: StatusDoc = TwitterDataProcessor.process_status(
                status=status)
            response_sent: SentimentAnalysisOutput = SentimentAnalysisOutput()

            # 2. Add additional parameters related to sentiment analysis
            if add_sentiment:
                if len(status_doc.text) >= TwitterDataProcessor.min_char:
                    response_sent: SentimentAnalysisOutput = TwitterDataProcessor.process_sentiment_analysis(
                        doc=status_doc.text)
            status_doc.sentiment_analysis: dict = response_sent.__dict__

            # 3. Get the user
            user: User = status.__getattribute__("user")
            user_doc: UserAccountDoc = TwitterDataProcessor.process_user(
                user=user)

            # 4. Add additional params
            if add_bot_analysis:
                response_botometer_analysis: BotometerAnalysisOutput = TwitterDataProcessor.process_botometer_analysis(
                    user_id=user_doc.id, twitter_credentials=twitter_credentials)
                user_doc.botometer_analysis: dict = response_botometer_analysis.__dict__

            # 5. Get the output
            output: TwitterDataOutput = TwitterDataOutput(
                status=status_doc.__dict__,
                user=user_doc.__dict__)
        except Exception as e:
            logger.error(e)
        return output

    @staticmethod
    def process_status(status: Status) -> StatusDoc:
        return StatusDoc(status=status)

    @staticmethod
    def process_user(user: User) -> UserAccountDoc:
        return UserAccountDoc(user=user)

    @staticmethod
    def process_sentiment_analysis(doc: str) -> SentimentAnalysisOutput:
        sentiment_output: SentimentAnalysisOutput = SentimentAnalysisOutput()
        try:
            flair_sent: FlairSentOutput = SentimentAnalysisAPI.get_flair_sentiment_analysis(
                doc=doc)
            textblob_sent: TextBlobSentOutput = SentimentAnalysisAPI.get_textblob_sentiment_analysis(
                doc=doc)
            nltk_sent: NLTKSentOutput = SentimentAnalysisAPI.get_nltk_sentiment_analysis(
                doc=doc)

            sentiment_output: SentimentAnalysisOutput = SentimentAnalysisOutput(
                flair_sent=flair_sent, textblob_sent=textblob_sent, nltk_sent=nltk_sent)
        except Exception as e:
            logger.error(e)
        return sentiment_output

    @staticmethod
    def process_botometer_analysis(user_id: int, twitter_credentials: dict) -> BotometerAnalysisOutput:
        output: BotometerAnalysisOutput = BotometerAnalysisOutput()
        try:
            botometer_analysis_api: BotAnalysisAPI = BotAnalysisAPI(
                consumer_key=twitter_credentials.get("consumer_key"),
                consumer_secret=twitter_credentials.get("consumer_secret"),
                access_token=twitter_credentials.get("access_token"),
                access_token_secret=twitter_credentials.get("access_token_secret"),
                api_key=twitter_credentials.get("botometer_api_key"))
            output: BotometerAnalysisOutput = botometer_analysis_api.analyse_account_by_id(
                user_id=user_id)
        except Exception as e:
            logger.error(e)
        return output