from bson.objectid import ObjectId

import src.repository as db
from src.models.team import Team

collection = db.Collection.TEAM


def create_team(team: Team):
    return db.insert(collection, team)


def add_user(team_id: str, user_id: str):
    db.push(collection, ObjectId(team_id), 'users', ObjectId(user_id))


def remove_user(team_id: str, user_id: str):
    db.pull(collection, ObjectId(team_id), 'users', ObjectId(user_id))
