import sys
import threading
from helper.settings import logger, global_streaming_threads
from fandango_models.source_credibility_models import GeneralAPIResponse


class StreamingThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class ThreadsProcessor(object):

    @staticmethod
    def get_available_threads() -> list:
        return global_streaming_threads

    @staticmethod
    def start_new_streaming_process(thread_name: str, target_func: any,
                                    params: tuple = ()) -> GeneralAPIResponse:
        response: GeneralAPIResponse = object.__new__(GeneralAPIResponse)
        try:
            add_thread = True
            message: str = f"Thread {thread_name} was created with success!"
            status_code: int = 200
            stream_threads: list = ThreadsProcessor.get_available_threads()

            # If the list of threads is not empty
            if stream_threads:
                # Check if there is a thread with the same name running
                thread_names = [i.name for i in stream_threads]

                # Thread with the same name
                if thread_name in thread_names:
                    thread_idx = thread_names.index(thread_name)
                    current_thread: StreamingThread = stream_threads[thread_idx]

                    # If it is still alive
                    if current_thread.is_alive():
                        add_thread = False
                        message: str = f"Thread {thread_name} already running"
                        status_code: int = 202
                    else:
                        # remove old thread from list
                        global_streaming_threads.pop(thread_idx)
                        message: str = f"Thread {thread_name} was stopped and it will be removed"
                        status_code: int = 300

            if add_thread:
                streaming_thread = ThreadsProcessor.create_new_streaming_thread(
                    thread_name=thread_name,
                    target_func=target_func,
                    params=params)

                # Save thread into list
                global_streaming_threads.append(streaming_thread)

            response: GeneralAPIResponse = GeneralAPIResponse(
                message=message, status_code=status_code, data={})
        except Exception as e:
            logger.error(e)
        return response

    @staticmethod
    def create_new_streaming_thread(thread_name: str, target_func: any, params: tuple) -> StreamingThread:
        streaming_thread: StreamingThread = object.__new__(StreamingThread)
        try:
            # Create new thread
            streaming_thread: StreamingThread = StreamingThread(
                name=thread_name, target=target_func, args=params)
            # Start thread process
            streaming_thread.start()
        except Exception as e:
            logger.error(e)
        return streaming_thread

    @staticmethod
    def kill_streaming_thread(streaming_thread: StreamingThread) -> GeneralAPIResponse:
        response: GeneralAPIResponse = object.__new__(GeneralAPIResponse)
        try:
            # Still alive then kill it
            if streaming_thread.is_alive():
                streaming_thread.kill()
                streaming_thread.join()
                message: str = f"Thread {streaming_thread.name} was killed!"
                status_code: int = 200
                logger.warning(f"Thread {streaming_thread.name} was killed!")
            else:
                message: str = f"Thread {streaming_thread.name} is not alive!"
                status_code: int = 400
            response: GeneralAPIResponse = GeneralAPIResponse(
                message=message, status_code=status_code, data={})
        except Exception as e:
            logger.error(e)
        return response

    @staticmethod
    def stop_streaming_process(thread_name: str):
        response: GeneralAPIResponse = object.__new__(GeneralAPIResponse)
        try:
            not_found = True
            stream_threads: list = ThreadsProcessor.get_available_threads()

            # If the list of threads is not empty
            if stream_threads:
                # Check if there is a thread with the same name running
                thread_names = [i.name for i in stream_threads]

                # Thread with the same name
                if thread_name in thread_names:
                    thread_idx = thread_names.index(thread_name)
                    # Stop selected thread
                    current_thread: StreamingThread = stream_threads[thread_idx]
                    response_kill: GeneralAPIResponse = ThreadsProcessor.kill_streaming_thread(
                        streaming_thread=current_thread)
                    if response_kill.status_code == 200:
                        # Remove from list
                        stream_threads.pop(thread_idx)
                        not_found = False
            # Check not found
            if not_found:
                status_code: int = 400
                message: str = f"Thread {thread_name} was not found!"
            else:
                status_code: int = 400
                message: str = f"Thread {thread_name} was not found!"

            response: GeneralAPIResponse = GeneralAPIResponse(
                message=message, status_code=status_code, data={})
        except Exception as e:
            logger.error(e)
        return response

    @staticmethod
    def clean_threads():
        try:
            logger.info(f"Cleaning all threads")
            for i, thread_name in enumerate(global_streaming_threads):
                global_streaming_threads.pop(i)
        except Exception as e:
            logger.error(e)
