from twitter_processors.streaming_processor import StreamingProcessor
from connectors.twitter_api_connector import TwitterConnector
from helper.settings import consumer_key, consumer_secret, access_token, access_token_secret


if __name__ == '__main__':

    db_name: str = "test_twitter_v5"
    collection_name: str = "test_collection"
    data = {"languages": ["fr", "en"], "track": ["COVID"],
            "storage": "elasticsearch",
            "collection_names": {"status": f"tweets",
                                 "user": "users"},
            "mongo_db_name": db_name}

    # Set up the object
    twitter_connector: TwitterConnector = TwitterConnector(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret)

    # Twitter API Connection
    twitter_connector.set_up_twitter_api_connection()

    # Processing data
    streaming_processor: StreamingProcessor = StreamingProcessor(
        api=twitter_connector.api,
        languages=data.get("languages", ["en"]),
        track=data.get("track", ["COVID"]),
        db_name=db_name,
        collection_names=data.get("collection_names", ["test_collection"]),
        storage=data.get("storage", ["elasticsearch"]),
        add_sentiment=True,
        add_bot_analysis=True)

    streaming_processor.run_twitter_streaming()
