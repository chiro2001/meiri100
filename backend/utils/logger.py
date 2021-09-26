import logging
import os
import platform

from colorlog import ColoredFormatter
from logging import handlers

# Config Logging
LOGGER_FILENAME = './logs/gbk.log'
LOGGER_WHEN = 'midnight'


def get_logger(name=__name__):
    logger_base = logging.getLogger(name)
    logger_base.setLevel(logging.DEBUG)
    color_formatter = ColoredFormatter('%(log_color)s[%(module)-15s][%(funcName)-15s][%(levelname)-7s] %(message)s')
    try:
        handler = handlers.TimedRotatingFileHandler(filename=LOGGER_FILENAME,
                                                    when=LOGGER_WHEN)
    except FileNotFoundError:
        handler = handlers.TimedRotatingFileHandler(filename=os.path.join('..', LOGGER_FILENAME),
                                                    when=LOGGER_WHEN)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('[%(module)-15s][%(funcName)-15s][%(levelname)-7s] %(message)s'))
    logger_base.addHandler(handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formatter)
    stream_handler.setLevel(logging.INFO)
    logger_base.addHandler(stream_handler)
    return logger_base


logger = get_logger(__name__)
# logger.setLevel(logging.INFO)
# logging.basicConfig()
