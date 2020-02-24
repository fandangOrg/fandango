# -*- coding: utf-8 -*-

# ====================================================================================
# ------------------------- GLOBAL VARIABLES PREPROCESSING ---------------------------
# ====================================================================================

newspaper = None
thread = None
service = None


def init():
    """ Init method: Initialises the global variables required in the preprocessing step
    """
    global thread
    global service

    thread = None
    service = None