from pymongo import collection
from models.invitation import Invitation
import mongo as db

collection = db.Collection.INVITATION
    
def addInvitation(invitation: Invitation):
    return str(db.insert_one(invitation.__dict__, collection).inserted_id)

def get_invitation(id: str):
    result = db.find_one( id, collection )
    if result is not None:
        return Invitation.from_dict(result)
    return

def delete_invitation(id: str): 
    db.delete_document(id, collection)