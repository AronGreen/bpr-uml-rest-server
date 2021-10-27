from enum import Enum
from datetime import datetime

import src.repository as db
from src.models.log_item import LogItem


class LogLevel(Enum):
    ERROR = 'error'
    DEBUG = 'debug'
    INFO = 'info'


def log_debug(content, note: str):
    log(content, note, LogLevel.DEBUG)


def log_error(content, note: str):
    log(content, note, LogLevel.ERROR)


def log_info(content, note: str):
    log(content, note, LogLevel.INFO)


def log(content, note: str, log_level: LogLevel):
    if note is None:
        note = ''
    item = LogItem(
        _id=None,
        timestamp=str(datetime.now()),
        utc_timestamp=str(datetime.utcnow()),
        log_level=repr(log_level),
        note=note,
        content=repr(content))
    db.insert(db.Collection.DEBUG_LOG, item)
