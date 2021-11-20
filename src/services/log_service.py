from enum import Enum
from datetime import datetime

from bpr_data.repository import Repository, Collection
from bpr_data.models.log_item import LogItem

import settings

db = Repository.get_instance(**settings.MONGO_CONN)


class LogLevel(Enum):
    ERROR = 'error'
    DEBUG = 'debug'
    INFO = 'info'


def log_debug(content, note: str) -> None:
    log(content, note, LogLevel.DEBUG)


def log_error(content, note: str) -> None:
    log(content, note, LogLevel.ERROR)


def log_info(content, note: str) -> None:
    log(content, note, LogLevel.INFO)


def log(content, note: str, log_level: LogLevel) -> None:
    if note is None:
        note = ''
    item = LogItem(
        _id=None,
        timestamp=str(datetime.now()),
        utcTimestamp=str(datetime.utcnow()),
        logLevel=repr(log_level),
        note=note,
        content=repr(content))
    db.insert(Collection.APPLICATION_LOG, item)
