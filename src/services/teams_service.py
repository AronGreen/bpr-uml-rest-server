from bson.objectid import ObjectId
from flask import abort

from bpr_data.repository import Repository, Collection
from bpr_data.models.team import Team, TeamUser

from src.services import workspace_service
from src.util import list_util
import settings

db = Repository.get_instance(
    protocol=settings.MONGO_PROTOCOL,
    default_db=settings.MONGO_DEFAULT_DB,
    pw=settings.MONGO_PW,
    host=settings.MONGO_HOST,
    user=settings.MONGO_USER)

collection = Collection.TEAM


def create_team(team: Team) -> Team:
    workspace = workspace_service.get_workspace(workspace_id=team.workspaceId)
    if workspace is None:
        abort(404, description='Workspace not found')
    insert_result = db.insert(collection, team)
    if insert_result is not None:
        return Team.from_dict(insert_result)


def add_users(team_id: str, team_users: list) -> Team:
    team = get_team(ObjectId(team_id))
    if team is None:
        abort(404, description="Team not found")
    list_util.ensure_no_duplicates(team_users, "userId")
    if not workspace_service.are_users_in_workspace(workspace_id=team.workspaceId,
                                                    user_ids=[user.userId for user in team_users]):
        abort(400)
    for user_to_add in team_users:
        for team_user in team.users:
            if user_to_add.userId == team_user.userId:
                abort(400)
    items = TeamUser.as_dict_list(team_users)
    db.push_list(collection=collection, document_id=team._id, field_name='users', items=items)
    return get_team(team_id=team._id)


def get_team(team_id: ObjectId):
    find_result = db.find_one(collection=collection, _id=team_id)
    if find_result is not None:
        team = Team.from_dict(find_result)
        team.users = TeamUser.from_dict_list(team.users)
        return team


def remove_user(team_id: str, user_id: str) -> bool:
    return db.pull(collection, ObjectId(team_id), 'users', ObjectId(user_id))
