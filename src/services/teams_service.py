from bpr_data.models.project import Project
from bson.objectid import ObjectId
from flask import abort

from bpr_data.repository import Repository, Collection
from bpr_data.models.team import Team, TeamUser

from src.services import workspace_service
from src.util import list_util
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

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


def replace_users(team_id: str, team_users: list) -> Team:
    team = get_team(ObjectId(team_id))
    if team is None:
        abort(404, description="Team not found")

    if len(team_users) > 0:
        list_util.ensure_no_duplicates(team_users, "userId")
        if not workspace_service.are_users_in_workspace(workspace_id=team.workspaceId,
                                                        user_ids=[user.userId for user in team_users]):
            abort(400)

    team.users = team_users
    db.update(Collection.TEAM, team)
    return get_team_with_user_details(ObjectId(team_id))


def get_team(team_id: ObjectId):
    find_result = db.find_one(collection=collection, _id=team_id)
    if find_result is not None:
        team = Team.from_dict(find_result)
        team.users = TeamUser.from_dict_list(team.users)
        return team


def remove_user(team_id: str, user_id: str) -> bool:
    return db.pull(collection, ObjectId(team_id), 'users', ObjectId(user_id))


def get_team_with_user_details_for_user(team_id: ObjectId, firebase_id: str) -> Team:
    team = get_team(team_id=team_id)
    workspace_service.get_workspace_for_user(workspace_id=team.workspaceId, firebase_id=firebase_id)
    return get_team_with_user_details(team_id=team_id)


def get_team_with_user_details(team_id: ObjectId) -> Team:
    pipeline = [
        {'$match': {'_id': team_id}},
        __make_unwind_step('$users'),
        {
            '$lookup': {
                'from': 'user',
                'localField': 'users.userId',
                'foreignField': '_id',
                'as': 'users.user'
            }
        },
        __make_unwind_step('$users.user'),
        {'$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'workspaceId': {'$first': '$workspaceId'},
            'users': {'$addToSet': '$users'}
        }}
    ]
    results = db.aggregate(collection=Collection.TEAM,
                           pipeline=pipeline,
                           return_type=Team)
    if len(results) > 0:
        return results[0]


def __make_unwind_step(path: str, preserve_null_and_empty_arrays: bool = True) -> dict:
    return {
        '$unwind':
            {
                'path': path,
                'preserveNullAndEmptyArrays': preserve_null_and_empty_arrays
            }
    }


def update_team_name(team_id: ObjectId, name: str):
    team = get_team(team_id=team_id)
    if team is None:
        abort(404, description="Team not found")
    team.name = name
    db.update(collection=collection, item=team)
    return get_team(team_id=team_id)


def delete_team(team_id: ObjectId):
    db.delete(collection=collection, _id=team_id)
    db.cleanup_relations(collection.PROJECT, 'teams', {'teamId': team_id})
    return "ok"


def check_teams_belong_to_workspace(team_ids: list, workspace_id: ObjectId):
    for team_id in team_ids:
        team = Team.from_dict(db.find_one(collection=collection, _id=team_id))
        if team.workspaceId != workspace_id:
            abort(405)


def get_teams_for_user(user_id: str) -> list:
    find_result = db.find(collection=collection, nested_conditions={'users.userId': user_id})
    if find_result is not None:
        return Team.from_dict_list(find_result)
    else:
        return []
