from src.models.mongo_document_base import MongoDocumentBase
from dataclasses import dataclass
from bson.objectid import ObjectId


@dataclass
class User(MongoDocumentBase):
    user_name: str
    email: str
    user_id: ObjectId
