from enum import Enum
from datetime import datetime
import mongo as db


class LogLevel(Enum):
    ERROR = 'error'
    DEBUG = 'debug'
    INFO = 'info'


def log_debug(content, note: str):
    log(content, note, LogLevel.DEBUG)


def log_error(content, note: str):
    log(content, note, LogLevel.ERROR)


def log_error(content, note: str):
    log(content, note, LogLevel.INFO)


def log(content, note: str, log_level: LogLevel):
    if note is None:
        note = ''
    item = {
        'timestamp': str(datetime.now()),
        'utc_timestamp': str(datetime.utcnow()),
        'log_level' : repr(log_level),
        'note': note,
        'content':repr(content)
    }
    db.insert_one(item, db.Collection.DEBUG_LOG)