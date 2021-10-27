from src.models.mongo_document_base import MongoDocumentBase
from dataclasses import dataclass


@dataclass
class LogItem(MongoDocumentBase):
    timestamp: str
    utc_timestamp: str
    log_level: str
    note: str
    content: str
