from bson import ObjectId

from src.models.invitation import Invitation
import src.util.email_utils as email_utils
import src.services.email_service as email_service
import src.services.workspace_service as workspace_service
import src.repository as db
from src.models.team import Team
from src.models.user import User

collection = db.Collection.USER


def invite_user(invitation: Invitation) -> str:
    if email_utils.is_valid(invitation.inviteeEmailAddress):
        workspace_name = workspace_service.get_workspace_name(invitation.workspaceId)
        subject = "Diagramz invitation"
        message = f"{invitation.inviterId} sent you an invitation on Diagramz to collaborate on {workspace_name}"
        return email_service.send_email(invitation.inviteeEmailAddress, subject, message)


def get_user(userId: str) -> User:
    find_result = db.find_one(collection, id=userId)
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


def get_teams_for_user(user_id: str) -> list:
    find_result = db.find(db.Collection.TEAM, firebaseId=user_id)
    if find_result is not None:
        return Team.from_dict_list(find_result)


def get_user_by_firebase_id(firebase_id: str) -> User:
    find_result = db.find_one(collection, firebaseId=firebase_id)
    if find_result is not None:
        return User.from_dict(find_result)


def get_user_by_email_address(email: str) -> User:
    find_result = db.find_one(collection, email=email)
    if find_result is not None:
        return User.from_dict(find_result)
