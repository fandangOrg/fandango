from twitter_processors.searching_processor import SearchingProcessor
from connectors.twitter_api_connector import TwitterConnector
from helper.settings import consumer_key, consumer_secret, access_token, access_token_secret


if __name__ == '__main__':

    mongo_db_name: str = "Climate_change"
    collection_names: dict = {"status": "tweets", "user": "users"}
    local_storage: str = "D:\\DAVID\\Datasets\\COVID_19_tweets"
    #"D:\\DAVID\\Datasets\\Climate_change_tweets"
    dest_storage: str = "elasticsearch"

    twitter_connector: TwitterConnector = TwitterConnector(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret)

    searching_processor: SearchingProcessor = SearchingProcessor(
        twitter_connector=twitter_connector,
        db_name=mongo_db_name,
        collection_names=collection_names,
        local_storage=local_storage,
        dest_storage=dest_storage)

    searching_processor.run_twitter_searching()
