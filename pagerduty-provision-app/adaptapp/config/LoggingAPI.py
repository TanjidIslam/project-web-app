import logging


class LoggerAPIConfig(object):
    # Logging library
    
    log = logging.getLogger()
    console = logging.StreamHandler()
    log.addHandler(console)
    format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    console.setFormatter(logging.Formatter(format_str))