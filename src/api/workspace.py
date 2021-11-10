from flask import Blueprint, request, g, abort

from flask.wrappers import Response

from src.models.invitation import Invitation
from src.models.user import User
from src.models.workspace import Workspace
from src.services import workspace_service, users_service, project_service

api = Blueprint('workspace_api', __name__)


@api.route("", methods=['POST'])
def create_workspace():
    request_data = request.get_json()
    print(request_data, flush=True)
    if 'name' in request_data:
        to_create = Workspace(
            _id=None,
            creatorId=g.firebase_id,
            name=request_data['name'],
            users=[g.firebase_id])
        created = workspace_service.create_workspace(to_create)
        return Response(created.as_json(), mimetype="application/json")
    abort(400, description="Workspace name needed")


@api.route("", methods=['GET'])
def get_workspaces():
    user_id = g.firebase_id
    data = workspace_service.get_user_workspaces(user_id)
    result = Workspace.as_json_list(data)
    return Response(result, mimetype="application/json")


@api.route("/<workspaceId>", methods=['GET'])
def get_workspace(workspaceId: str):
    result = workspace_service.get_workspace(workspaceId)
    return Response(result.as_json(), mimetype="application/json")


@api.route("/<workspaceId>/users", methods=['GET'])
def get_workspace_users(workspaceId: str):
    result = workspace_service.get_workspace_users(workspaceId)
    return Response(User.as_json_list(result), mimetype="application/json")


@api.route("/<workspaceId>/projects", methods=['GET'])
def get_workspace_user_projects(workspaceId: str):
    user_id = users_service.get_user_by_firebase_id(g.firebase_id).id
    result = project_service.get_user_projects(workspaceId, user_id)
    return Response(User.as_json_list(result), mimetype="application/json")


@api.route("/invitation", methods=['POST'])
def invite_user():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        invitation = Invitation(
            _id=None,
            inviterId=g.firebase_id,
            workspaceId=request_data['workspaceId'],
            inviteeEmailAddress=request_data['inviteeEmailAddress'])
        result = workspace_service.invite_user(invitation)
        return Response(status=200, response=result, mimetype="application/json")
    return Response("Workspace id and invitee email address are required", mimetype="application/json")


# TODO: remember to check for permissions when we get to that part
@api.route("/user", methods=['PATCH'])
def remove_user_from_workspace():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'userId' in request_data:
        if workspace_service.remove_workspace_user(
            request_data['workspaceId'],
            request_data['userId']):
            return Response(status=200)
        else:
            abort(500, description="Something went wrong")
    return abort(400, descriptioin="Workspace id and/or user id missing")


@api.route("/invitation/response", methods=['POST'])
def respond_to_invitation():
    request_data = request.get_json()
    if 'invitationId' in request_data and 'accepted' in request_data:
        invitation_id = request_data['invitationId']
        accepted = request_data['accepted']
        return Response(status=200, response=workspace_service.respond_to_invitation(invitation_id, accepted))
    return "Workspace id and user id"

