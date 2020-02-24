# -*- coding: utf-8 -*-
import queue
from threading import Event

# ====================================================================================
# ------------------------- GLOBAL VARIABLES Graph analysis---------------------------
# ====================================================================================

thread = None
thread_neo4j = None
queue_neo4j = None
event = None


def init():
    """ Init method: Initialises the global variables required in the graph analysis
    """
    global thread
    global thread_neo4j
    global event
    global queue_neo4j

    thread = None
    thread_neo4j = None
    event = Event()
    queue_neo4j = queue.Queue()