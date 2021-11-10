from flask import Blueprint, request, abort, Response

from src.services import teams_service as service
from src.models.team import Team

api = Blueprint('teams_api', __name__)


# when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_team():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'teamName' in request_data:
        created = service.create_team(Team.from_json(request_data))
        if created is not None:
            return Response(created.as_json(), mimetype="application/json")
        else:
            return Response('{}', mimetype="application/json")
    return "properties missing"


@api.route("/users", methods=['POST'])
def add_users():
    request_data = request.get_json()
    if 'teamId' in request_data and 'userIds' in request_data:
        team_id = request_data['teamId']
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.add_user(team_id, user_id)
        return Response('{}', mimetype="application/json")
    abort(400)


@api.route("/users", methods=['DELETE'])
def remove_user():
    request_data = request.get_json()
    if 'teamId' in request_data and 'userIds' in request_data:
        team_id = request_data['teamId']
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.remove_user(team_id, user_id)
        return Response('{}', mimetype="application/json")
    abort(400)
