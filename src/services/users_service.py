from bpr_data.models.workspace import Workspace
from bson import ObjectId

from bpr_data.models.invitation import Invitation
from bpr_data.repository import Repository, Collection
from bpr_data.models.team import Team
from bpr_data.models.user import User

import src.util.email_utils as email_utils
import src.services.email_service as email_service
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.USER


def invite_user(invitation: Invitation) -> str:
    if email_utils.is_valid(invitation.inviteeEmailAddress):
        workspace_name = db.find_one(Collection.WORKSPACE, _id=invitation.workspaceId, return_type=Workspace).name
        subject = "Diagramz invitation"
        message = f"{invitation.inviterId} sent you an invitation on Diagramz to collaborate on {workspace_name}"
        return email_service.send_email(invitation.inviteeEmailAddress, subject, message)


def get_user(userId: ObjectId) -> User:
    find_result = db.find_one(collection, _id=userId)
    if find_result is not None:
        return User.from_dict(find_result)


def get_user_name(userId: str) -> str:
    user = get_user(userId)
    if user is not None:
        return user.name


def add_user(user: User) -> User:
    # TODO: Check if user already exists.
    inserted = db.insert(collection, user)
    if inserted is not None:
        return User.from_dict(inserted)

def get_user_by_firebase_id(firebase_id: str) -> User:
    find_result = db.find_one(collection, firebaseId=firebase_id)
    if find_result is not None:
        return User.from_dict(find_result)


def get_user_by_email_address(email: str) -> User:
    find_result = db.find_one(collection, email=email)
    if find_result is not None:
        return User.from_dict(find_result)
