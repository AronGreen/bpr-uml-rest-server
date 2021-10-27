from src.models.invitation import Invitation
import src.util.email_utils as email
import src.services.email_service as email_service
import src.services.workspace_service as workspace_service
import src.repository as db
from src.models.user import User

userCollection = db.Collection.USER


def invite_user(invitation: Invitation):
    if email.is_valid(invitation.invitee_email_address):
        workspace_name = workspace_service.get_workspace_name(invitation.workspace_id)
        subject = "Diagramz invitation"
        message = f"{invitation.user_name} sent you an invitation on Diagramz to collaborate on {workspace_name}"
        return email_service.send_email(invitation.invitee_email_address, subject, message)


def get_user(userId):
    return User.from_dict(db.find_one(userCollection, _id=userId))


def get_user_name(userId):
    return get_user(userId).user_name


def add_user(user: User):
    return db.insert(userCollection, user)
