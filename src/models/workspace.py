from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class Workspace(MongoDocumentBase):
    creatorId: ObjectId
    workspace_name: str
    users: list
