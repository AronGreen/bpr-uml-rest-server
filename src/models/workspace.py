from src.models.mongo_document_base import MongoDocumentBase
from dataclasses import dataclass
from bson.objectid import ObjectId


@dataclass
class Workspace(MongoDocumentBase):
    creator_id: ObjectId
    workspace_name: str
