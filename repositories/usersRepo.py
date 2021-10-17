from pymongo import collection
from models.user import User
import mongo as db

collection = db.Collection.USER
    
def addUser(user):
    return str(db.insert_one(user.__dict__, collection).inserted_id)

def getUserByFirebaseId(user_id: str):
    result = list(db.find_from_query({"user_id": user_id}, collection))
    if len(result) == 1:
        return result[0]
    return None