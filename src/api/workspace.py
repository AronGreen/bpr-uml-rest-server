from flask import Blueprint, request, g, abort

from flask.wrappers import Response

from src.models.invitation import Invitation
from src.models.workspace import Workspace
import src.services.workspace_service as workspace_service

api = Blueprint('workspace_api', __name__)


@api.route("/", methods=['POST'])
def create_workspace():
    request_data = request.get_json()
    print(request_data, flush=True)
    if 'workspaceName' in request_data:
        to_create = Workspace(
            _id=None,
            creatorId=g.user_id,
            workspaceName=request_data['workspaceName'],
            users=list())
        created = workspace_service.create_workspace(to_create)
        return created.as_json()
    abort(400)


@api.route("/", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = workspace_service.get_user_workspaces(user_id)
    result = Workspace.as_json_list(data)
    return Response(result, mimetype="application/json")


@api.route("/invitation", methods=['POST'])
def invite_user():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        invitation = Invitation(
            _id=None,
            inviterId=g.user_id,
            workspaceId=request_data['workspaceId'],
            inviteeEmailAddress=request_data['inviteeEmailAddress'])
        result = workspace_service.invite_user(invitation)
        return Response(result, mimetype="application/json")
    return Response("Workspace id and invitee email address are required", mimetype="application/json")


# TODO: remember to check for permissions when we get to that part
@api.route("/user", methods=['PATCH'])
def remove_user_from_workspace():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'userId' in request_data:
        return workspace_service.remove_workspace_user(
            request_data['workspaceId'],
            request_data['userId'])
    return "Workspace id and/or user id missing"


@api.route("/invitation/response", methods=['POST'])
def respond_to_invitation():
    request_data = request.get_json()
    if 'invitationId' in request_data and 'accepted' in request_data:
        invitation_id = request_data['invitationId']
        accepted = request_data['accepted']
        return workspace_service.respond_to_invitation(invitation_id, accepted)
    return "Workspace id and user id"
