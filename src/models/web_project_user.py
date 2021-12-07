from dataclasses import dataclass

from bpr_data.models.user import User

@dataclass
class WebProjectUser(User):
    isProjectManager: bool
    isEditor: bool

    @classmethod
    def from_project_user(cls, user: dict):
        return WebProjectUser(_id = user["user"]["_id"], name=user["user"]["name"], email=user["user"]["email"], firebaseId=user["user"]["firebaseId"], isEditor=user["isEditor"], isProjectManager=user["isProjectManager"])