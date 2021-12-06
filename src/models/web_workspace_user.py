from dataclasses import dataclass

from bson.objectid import ObjectId

from bpr_data.models.mongo_document_base import SerializableObject
from bpr_data.models.user import User

@dataclass
class WebWorkspaceUser(SerializableObject):
    user: User
    permissions: list