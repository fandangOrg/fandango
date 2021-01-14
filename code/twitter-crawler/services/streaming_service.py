from helper.settings import logger
from data_models.api_models import StreamingProcessOutput, StreamingServiceOutput
from api.api import TWStreamingAPI


class TwitterStreamingService:
    def __init__(self, languages: list, track: list, storage: str, mongo_db_name: str = "default"):
        self.languages: list = languages
        self.track: list = track
        self.storage: str = storage
        self.mongo_db_name: str = mongo_db_name
        self.twst_api: TWStreamingAPI = TWStreamingAPI()

    def set_storage(self, storage: str):
        self.storage: str = storage

    def set_track(self, track: list):
        self.track: list = track

    def set_languages(self, languages: list):
        self.languages: list = languages

    def set_mongo_db_name(self, mongo_db_name: str):
        self.mongo_db_name: str = mongo_db_name

    def start_streaming(self, thread_name: str, collection_name: str = "default",
                        es_index_name: str = "default") -> StreamingServiceOutput:
        output: StreamingServiceOutput = object.__new__(StreamingServiceOutput)
        try:
            set_name: str = collection_name if self.storage == "mongoDB" else es_index_name
            data = {"languages": self.languages,
                    "track": self.track,
                    "storage": self.storage,
                    "collection_names": {"status": f"{set_name}_tweets",
                                         "user": "users"},
                    "mongo_db_name": self.mongo_db_name}

            response: StreamingProcessOutput = self.twst_api.start_new_streaming_process(
                thread_name=thread_name, data=data)

            # Generate the response
            output: StreamingServiceOutput = StreamingServiceOutput(
                status_code=response.status_code, message=response.message, data=response.data)
        except Exception as e:
            logger.error(e)
        return output

    def stop_streaming(self, es_index: str) -> StreamingServiceOutput:
        output: StreamingServiceOutput = object.__new__(StreamingServiceOutput)
        try:
            # 1. Stop streaming
            response: StreamingProcessOutput = self.twst_api.stop_streaming_process(
                thread_name=es_index)

            # 2. Generate the response
            output: StreamingServiceOutput = StreamingServiceOutput(
                status_code=response.status_code, message=response.message, data=response.data)
        except Exception as e:
            logger.error(e)
        return output

