from src.models.mongo_document_base import MongoDocumentBase
from dataclasses import dataclass
from typing import Optional


@dataclass
class SomeItem(MongoDocumentBase):
    number: int
    text: str
    users: list
    random: Optional[str] = None


