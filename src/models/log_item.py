from dataclasses import dataclass
from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class LogItem(MongoDocumentBase):
    timestamp: str
    utc_timestamp: str
    log_level: str
    note: str
    content: str
