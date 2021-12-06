from dataclasses import dataclass
from os import name
from bpr_data.models.mongo_document_base import SerializableObject

from bpr_data.models.user import User

@dataclass
class WebWorkspaceUser(User):
    permissions: list

    @classmethod
    def from_workspace_user(cls, user: dict):
        return WebWorkspaceUser(_id = user["user"]["_id"], name=user["user"]["name"], email=user["user"]["email"], firebaseId=user["user"]["firebaseId"], permissions=user["permissions"])