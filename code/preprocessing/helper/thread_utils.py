from helper import global_variables as gv
from helper.streaming_thread import StreamingThread
from typing import Optional


def kill_streaming_thread(streaming_thread: StreamingThread):
    response = False
    try:
        # Still alive then kill it
        if streaming_thread.is_alive():
            streaming_thread.kill()
            streaming_thread.join()
            response = True
            gv.logger.warning("Thread %s was killed!", str(streaming_thread.name))
    except Exception as e:
        gv.logger.error(e)
    return response


def start_offline_process(thread_name: str, target_func):
    response: dict = {"message": gv.http_response_500, "code": 500}
    try:
        add_thread = True
        message: str = gv.http_response_200
        code: int = 200
        # If the list of threads is not empty
        if gv.offline_threads:
            # Check if there is a thread with the same name running
            thread_names = [i.name for i in gv.offline_threads]
            # Thread with the same name
            if thread_name in thread_names:
                thread_idx = thread_names.index(thread_name)

                # If it is still alive
                if gv.offline_threads[thread_idx].is_alive():
                    add_thread = False
                    message: str = gv.http_response_400
                    code: int = 400
                else:
                    # remove old thread from list
                    gv.offline_threads.pop(thread_idx)
        if add_thread:
            streaming_thread: StreamingThread = create_new_streaming_thread(
                thread_name=thread_name,
                target_func=target_func)
            # Save thread into list
            gv.offline_threads.append(streaming_thread)

        response["message"] = message
        response["code"] = code

    except Exception as e:
        gv.logger.error(e)
    return response


def create_new_streaming_thread(thread_name: {str}, target_func):
    streaming_thread: Optional[StreamingThread] = None
    try:
        # Create new thread
        streaming_thread = StreamingThread(name=thread_name, target=target_func)
        # Start thread process
        streaming_thread.start()
    except Exception as e:
        gv.logger.error(e)
    return streaming_thread