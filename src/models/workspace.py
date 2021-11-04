from dataclasses import dataclass, field
from bson.objectid import ObjectId

from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class Workspace(MongoDocumentBase):
    creatorId: ObjectId
    name: str
    users: list
