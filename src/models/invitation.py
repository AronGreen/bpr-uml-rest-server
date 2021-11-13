from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase, SimpleMongoDocumentBase


@dataclass
class Invitation(MongoDocumentBase):
    inviterId: ObjectId
    workspaceId: ObjectId
    inviteeEmailAddress: str

@dataclass
class InvitationGetModel(Invitation):
    inviterUserName: str
    workspaceName: str
