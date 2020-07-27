import logging
import colorlog
import os
import time
import shutil
import sys


LOG_TYPES = ['CONSOLE', 'FILES', 'BOTH', 'NONE']
os.environ['app_logs'] = os.path.join('app_logs') # log folder


def check_directory_expired_date(total_time):
    try:
        parent_dir = os.getenv('app_logs')
        # If not exists
        if not os.path.exists(parent_dir):
            print('Created New APP Logs Folder')
            os.makedirs(parent_dir)
        else:
            # if exists check the date
            prev_date = os.path.getmtime(parent_dir)
            current_date = time.time()

            # Date has expired
            if int(current_date - prev_date) >= total_time:
                print('Updated APP Logs folder')
                try:
                    # Delete directory and create it again
                    shutil.rmtree(parent_dir)
                    os.makedirs(parent_dir)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)



def init_logger(logger_name, log_type, console_log_level, log_expiration_time) -> logging.Logger:

    # loggin library links:
    # http://zetcode.com/python/logging/
    # https://docs.python.org/3/howto/logging.html
    # https://docs.python.org/3/library/logging.handlers.html
    # https://docs.python.org/3/library/logging.html

    if log_type.upper() not in LOG_TYPES:
        raise ValueError('Invalid log type: %s. Allowed only: FILES, CONSOLE, BOTH or NONE' % log_type)


    logger = logging.getLogger(logger_name)


    if log_type.upper() == 'NONE':
        logger.setLevel(logging.CRITICAL)
        return logger


    if log_type == 'CONSOLE':
        # get the console log level
        numeric_log_level = getattr(logging, console_log_level.upper(), None)
        if not isinstance(numeric_log_level, int):
            raise ValueError('Invalid console log level: %s' % console_log_level)

        # set the log level of logger (for the console)
        logger.setLevel(numeric_log_level)


    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(funcName)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
    )

    colorlog.basicConfig(format=colorlog_format)


    if log_type == 'FILES' or log_type == 'BOTH':

        # reset the default handler of the root logger
        # All loggers are descendants of the root logger. Each logger passes log messages on to its parent
        logging.getLogger().handlers = []

        # set the log level of logger (lower level to write all in the files)
        logger.setLevel(logging.DEBUG)

        # Manages console logs
        if log_type == 'BOTH':
            # get the console log level
            numeric_log_level = getattr(logging, console_log_level.upper(), None)
            if not isinstance(numeric_log_level, int):
                raise ValueError('Invalid console log level: %s' % console_log_level)

            sh = logging.StreamHandler(stream=sys.stderr)
            sh.setLevel(numeric_log_level)
            formatter = colorlog.ColoredFormatter(colorlog_format)
            sh.setFormatter(formatter)
            logger.addHandler(sh)


        # Manages file logs

        log_expiration_time_cast_error = False

        try:
            log_expiration_time_int = int(log_expiration_time)
        except ValueError:
            print('WARNING: The specified Log Expiration Time is invalid: "{0}". The default value will be used (2 hours)'.format(log_expiration_time))
            log_expiration_time_cast_error = True
            log_expiration_time_int = 2 # hours, 2 hours is considered the default value

        # create the log directory
        check_directory_expired_date(log_expiration_time_int * 36000)  # hours * (number of seconds in one hour)

        # Output full log
        log_path = os.path.join(os.getenv('app_logs'), 'app.log')
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Output warning log
        log_path_w = os.path.join(os.getenv('app_logs'), 'app.warning.log')
        fh = logging.FileHandler(log_path_w)
        fh.setLevel(logging.WARNING)
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Output error log
        log_path_e = os.path.join(os.getenv('app_logs'), 'app.error.log')
        fh = logging.FileHandler(log_path_e)
        fh.setLevel(logging.ERROR)
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # log the cast error if occurred above
        if log_expiration_time_cast_error:
            logger.warning('The specified Log Expiration Time is invalid: "{0}". The default value will be used (2 hours)'.format(
                    log_expiration_time))


    # print(logging.getLogger().handlers)
    # print(logger.handlers)


    return logger