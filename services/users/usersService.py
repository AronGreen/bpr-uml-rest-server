from pymongo import collection
from models.user import User
import repositories.usersRepo as repo
import mongo as db

collection = db.Collection.USER

def addUser(user: User):
    dbUser = repo.getUserByFirebaseId(user.user_id)
    if dbUser == None:
        return repo.addUser(user)
    return dbUser["user_id"]
    
def get_teams_for_user(user_id: str):
    db.find({""}, db.Collection.TEAM)