from bson.objectid import ObjectId

import src.repository as db
from src.models.team import Team

collection = db.Collection.TEAM


def create_team(team: Team) -> Team:
    insert_result = db.insert(collection, team)
    if insert_result is not None:
        return Team.from_dictionary(insert_result)


def add_user(team_id: str, user_id: str) -> bool:
    return db.push(collection, ObjectId(team_id), 'users', ObjectId(user_id))


def remove_user(team_id: str, user_id: str) -> bool:
    return db.pull(collection, ObjectId(team_id), 'users', ObjectId(user_id))
