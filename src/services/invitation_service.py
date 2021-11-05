from src.models.invitation import Invitation
import src.repository as db

collection = db.Collection.INVITATION


def add_invitation(invitation: Invitation) -> Invitation:
    insert_result = db.insert(collection, invitation)
    if insert_result is not None:
        return Invitation.from_dict(insert_result)


def get_invitation_by_id(invitation_id: str) -> Invitation:
    result = db.find_one(collection, id=invitation_id)
    if result is not None:
        return Invitation.from_dict(result)


def delete_invitation(invitation_id: str) -> bool:
    return db.delete(collection, id=invitation_id)

def get_invitation(workspace_id: str, invitee_email_address: str) -> Invitation:
    invitation = db.find_one(collection=collection, workspaceId=workspace_id, inviteeEmailAddress=invitee_email_address)
    if invitation is not None:
        return Invitation.from_dict(invitation)