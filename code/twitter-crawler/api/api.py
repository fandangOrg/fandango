from helper.settings import (logger, consumer_secret,
                             consumer_key, access_token,
                             access_token_secret)
from tweepy import API
from connectors.twitter_api_connector import TwitterConnector
from data_models.api_models import StreamingProcessOutput, GeneralAPIResponse
from helper.streaming_thread import ThreadsProcessor
from twitter_processors.streaming_processor import StreamingProcessor
from twitter_processors.searching_processor import SearchingProcessor


class TWStreamingAPI(object):
    def __init__(self):
        self.twitter_connector: TwitterConnector = TwitterConnector(
            consumer_key=consumer_key,consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret)

    def set_up_twitter_api(self) -> API:
        api: API = object.__new__(API)
        try:
            # Start connection to Twitter
            if self.twitter_connector.api is None:
                api: API = self.twitter_connector.set_up_twitter_api_connection()
            else:
                api: API = self.twitter_connector.api
        except Exception as e:
            logger.error(e)
        return api
    
    def start_new_streaming_process(self, thread_name: str,
                                    data: dict) -> StreamingProcessOutput:
        output: StreamingProcessOutput = object.__new__(StreamingProcessOutput)
        try:
            # 1. Generate Streaming Processor
            api: API = self.set_up_twitter_api()
            streaming_processor: StreamingProcessor = StreamingProcessor(
                api=api,
                languages=data.get("languages", []),
                track=data.get("track", []),
                storage=data.get("storage", "mongoDB"),
                collection_names=data.get("collection_names", {}),
                mongo_db_name=data.get("mongo_db_name", "default"))

            # 2. Create new Thread
            response: GeneralAPIResponse = ThreadsProcessor.start_new_streaming_process(
                thread_name=thread_name,
                target_func=streaming_processor.run_twitter_streaming)

            # 3. Generate Output
            output: StreamingProcessOutput = StreamingProcessOutput(
                message=response.message,
                status_code=response.status_code,
                data=response.data)
        except Exception as e:
            logger.error(e)
        return output

    def stop_streaming_process(self, thread_name: str) -> StreamingProcessOutput:
        output: StreamingProcessOutput = object.__new__(StreamingProcessOutput)
        try:
            # 1. Stop thread
            response: GeneralAPIResponse = ThreadsProcessor.stop_streaming_process(
                thread_name=thread_name)

            # 3. Generate Output
            output: StreamingProcessOutput = StreamingProcessOutput(
                message=response.message,
                status_code=response.status_code,
                data=response.data)
        except Exception as e:
            logger.error(e)
        return output


class TWSearchingAPI:
    def __init__(self):
        self.twitter_connector: TwitterConnector = TwitterConnector(
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret)

    def set_up_twitter_api(self) -> API:
        api: API = object.__new__(API)
        try:
            # Start connection to Twitter
            if self.twitter_connector.api is None:
                api: API = self.twitter_connector.set_up_twitter_api_connection()
            else:
                api: API = self.twitter_connector.api
        except Exception as e:
            logger.error(e)
        return api

    def start_new_searching_process(self, thread_name: str,
                                    data: dict) -> StreamingProcessOutput:
        output: StreamingProcessOutput = object.__new__(StreamingProcessOutput)
        try:
            # 1. Generate Streaming Processor
            api: API = self.set_up_twitter_api()

            searching_processor: SearchingProcessor = SearchingProcessor(
                twitter_connector=self.twitter_connector,
                mongo_db_name=data.get(""),
                collection_names=data.get(""),
                local_storage=data.get(""),
                dest_storage=data.get(""))

            # 2. Create new Thread
            response: GeneralAPIResponse = ThreadsProcessor.start_new_streaming_process(
                thread_name=thread_name,
                target_func=searching_processor.run_twitter_searching)

            # 3. Generate Output
            output: StreamingProcessOutput = StreamingProcessOutput(
                message=response.message,
                status_code=response.status_code,
                data=response.data)
        except Exception as e:
            logger.error(e)
        return output

    def stop_streaming_process(self, thread_name: str) -> StreamingProcessOutput:
        output: StreamingProcessOutput = object.__new__(StreamingProcessOutput)
        try:
            # 1. Stop thread
            response: GeneralAPIResponse = ThreadsProcessor.stop_streaming_process(
                thread_name=thread_name)

            # 3. Generate Output
            output: StreamingProcessOutput = StreamingProcessOutput(
                message=response.message,
                status_code=response.status_code,
                data=response.data)
        except Exception as e:
            logger.error(e)
        return output