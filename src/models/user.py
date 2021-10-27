from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class User(MongoDocumentBase):
    user_name: str
    email: str
    user_id: ObjectId
