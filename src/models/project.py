from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase


@dataclass
class Project(MongoDocumentBase):
    title: str
    workspaceId: ObjectId
    projectUsers: list
    projectTeams: list


@dataclass
class ProjectUser(MongoDocumentBase):
    userId: ObjectId
    isEditor: bool


@dataclass
class ProjectTeam(MongoDocumentBase):
    teamId: ObjectId
    isEditor: bool
