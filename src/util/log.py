import logging
import sys
from datetime import datetime


def getLogger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorFormatter())
    logger.handlers = [ch]
    return logger


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        reset = '\x1b[39m'
        red = '\x1b[31m'
        green = '\x1b[32m'
        yellow = '\x1b[33m'
        cyan = '\x1b[36m'
        darkgrey = '\x1b[90m'
        white = '\x1b[37m'
        time = datetime.strftime(datetime.now(), '%H:%M:%S')

        color = white
        if record.levelname == 'DEBUG':
            color = green
        if record.levelname == 'WARNING':
            color = yellow
        if record.levelname == 'ERROR':
            color = red

        return f"[{color}{record.levelname}{reset}] [{cyan}{record.name}{reset}] ({darkgrey}{time}{reset}) - {color}{record.getMessage()}{reset}"
