from src.models.mongo_document_base import MongoDocumentBase
from dataclasses import dataclass
from bson.objectid import ObjectId


@dataclass
class Invitation(MongoDocumentBase):
    user_name: str
    workspace_id: ObjectId
    invitee_email_address: str
