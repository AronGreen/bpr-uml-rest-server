from bson.objectid import ObjectId
import mongo as db
from models.team import Team

collection = db.Collection.TEAM

def create_team(team: Team):
    return str(db.insert_one(team.__dict__, collection).inserted_id)

def update_users(team_id: str, users: list):
    db.update_document({"_id": ObjectId(team_id)}, {"users": users}, collection)
    return "Team updated"