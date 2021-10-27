from dataclasses import dataclass
from bson import ObjectId

from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class Team(MongoDocumentBase):
    team_name: str
    workspace_id: ObjectId
    users: list