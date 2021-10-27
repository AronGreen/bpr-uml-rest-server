from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class Invitation(MongoDocumentBase):
    inviter_id: ObjectId
    workspace_id: ObjectId
    invitee_email_address: str
