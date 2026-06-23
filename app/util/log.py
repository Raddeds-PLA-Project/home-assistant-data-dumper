import datetime
import logging
from . import placeholders

logging.basicConfig(level=placeholders.LOG_LEVEL, format="radded_data_dumper.%(threadName)s: [%(levelname)s] at %(asctime)s : [%(message)s]")

def error(msg):
    logging.error(msg)

def warning(msg):
    logging.warning(msg)

def info(msg):
    logging.info(msg)

def toomuchinfo(msg):
    logging.debug(msg)