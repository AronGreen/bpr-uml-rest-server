from src.models.invitation import Invitation
import src.util.email as email
import src.services.email.email as email_service
import src.services.workspace_service as workspace_service
import src.repository as db

userCollection = db.Collection.USER


def invite_user(invitation: Invitation):
    if email.is_valid(invitation.inviteeEmailAddress):
        workspace_name = workspace_service.get_workspace_name(invitation.workspaceId)
        invitor_name = get_user_name(invitation.invitorId)
        subject = "Diagramz invitation"
        message = "{} sent you an invitation on Diagramz to collaborate on {}".format(invitor_name, workspace_name)
        return email_service.send_email(invitation.inviteeEmailAddress, subject, message)


def get_user_name(userId):
    return db.find_one(userCollection, _id=userId)["userName"]


def add_user(user):
    return db.insert(userCollection, user)
