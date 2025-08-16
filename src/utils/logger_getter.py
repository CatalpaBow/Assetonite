from logging import getLogger, StreamHandler, DEBUG ,Formatter,config
import logging
import json

is_already_setuped = False
def _logger_setup():
    with open('config/log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)

def get_logger(name : str):
    if not is_already_setuped:
        _logger_setup()
    return logging.getLogger(name)
