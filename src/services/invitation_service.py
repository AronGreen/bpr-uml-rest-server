from src.models.invitation import Invitation
import src.repository as db

collection = db.Collection.INVITATION


def add_invitation(invitation: Invitation):
    return str(db.insert(collection, invitation).inserted_id)


def get_invitation(invitation_id: str):
    result = db.find_one(collection, id=invitation_id)
    if result is not None:
        return Invitation.from_dict(result)
    return


def delete_invitation(invitation_id: str):
    db.delete(collection, id=id)