from dataclasses import dataclass
from bson.objectid import ObjectId
from src.models.mongo_document_base import MongoDocumentBase, SerializableObject


@dataclass
class Project(MongoDocumentBase):
    title: str
    workspaceId: ObjectId
    users: list  # ProjectUser
    teams: list  # ProjectTeam

@dataclass
class ObjectIdReferencer(SerializableObject):

    @classmethod
    def to_object_ids(cls, field_name: str, objects: list):
        for object in objects:
            setattr(object, field_name, ObjectId(getattr(object, field_name))) 
        return objects

@dataclass
class ProjectUser(ObjectIdReferencer):
    userId: ObjectId
    isEditor: bool


@dataclass
class ProjectTeam(ObjectIdReferencer):
    teamId: ObjectId
    isEditor: bool
