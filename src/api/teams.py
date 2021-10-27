from flask import Blueprint, g, request, abort

from src.services import teams_service as service
from src.models.team import Team

api = Blueprint('teams_api', __name__)


# when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("/", methods=['POST'])
def create_team():
    request_data = request.get_json()

    if 'workspaceId' in request_data and 'teamName' in request_data:
        return service.create_team(Team.from_json(request_data))
    return "Workspace name required"


@api.route("/users", methods=['POST'])
def add_user():
    request_data = request.get_json()
    # {
    #     'teamId': ObjectId as str,
    #     'userIds': firebaseUserId as str
    # }
    if 'teamId' in request_data and 'userId' in request_data:
        team_id = request_data['teamId']
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.add_user(team_id, user_id)
        return
    abort(400)


@api.route("/users", methods=['DELETE'])
def remove_user():
    request_data = request.get_json()
    # {
    #     'teamId': ObjectId as str,
    #     'userIds': firebaseUserId as str
    # }
    if 'teamId' in request_data and 'userId' in request_data:
        team_id = request_data['teamId']
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.remove_user(team_id, user_id)
        return
    abort(400)
