from src.models.invitation import Invitation
import src.repository as db

collection = db.Collection.INVITATION


def add_invitation(invitation: Invitation) -> Invitation:
    insert_result = db.insert(collection, invitation)
    if insert_result is not None:
        return Invitation.from_dict(insert_result)


def get_invitation(invitation_id: str) -> Invitation:
    result = db.find_one(collection, id=invitation_id)
    if result is not None:
        return Invitation.from_dict(result)


def delete_invitation(invitation_id: str) -> bool:
    return db.delete(collection, id=invitation_id)

def invitation_exists(workspace_id: str, invitee_email_address: str):
    return db.find_one(collection=collection, workspaceId=workspace_id, inviteeEmailAddress=invitee_email_address)