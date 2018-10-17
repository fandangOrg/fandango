'''
Created on 26 set 2018

@author: camila
'''

import logging
import os
from logging.handlers import RotatingFileHandler
from fake_news_detection.config.AppConfig import log_folder


def getLogger(module, logname=False):

    log_path = log_folder

    if not os.path.exists(log_path):
        os.makedirs(log_path) 
        
    if logname == False:
        fname = log_path + '/' + 'log.txt'
    else:
        fname = log_path + '/' + logname

    with open(fname, 'wb'):
        pass
    print(log_path)
    print(os.path.exists(log_path))
    logger = logging.getLogger(module)
    fhand = RotatingFileHandler(fname, maxBytes=200000000, backupCount=5)
    shand = logging.StreamHandler()

    formatter = logging.Formatter('(%(name)s) %(asctime)s %(levelname)s %(message)s')
    fhand.setFormatter(formatter)
    shand.setFormatter(formatter)

    logger.addHandler(fhand)
    logger.addHandler(shand)
    logger.setLevel(logging.DEBUG)

    return logger


if __name__ == '__main__':
    log = getLogger(__name__)
    log.debug('msg1')
    log.info('msg2')
    log.critical('msg3')
    log.warning('msg4')
    log.error('msg5')