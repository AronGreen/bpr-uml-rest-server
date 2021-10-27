from flask import Blueprint, request, g
import json

from flask.wrappers import Response

from src.models.invitation import Invitation
from src.models.workspace import Workspace
import src.services.workspace_service as workspace_service

api = Blueprint('workspace_api', __name__)


@api.route("/", methods=['POST'])
def create_workspace():
    request_data = request.get_json()['data']
    if 'creatorId' in request_data and 'workspaceName' in request_data:
        return workspace_service.create_workspace(Workspace(
            _id=None,
            creator_id=g.user_id,
            workspace_name=request_data['workspaceName'],
            users=list()
        ))
    return "Workspace name required"


@api.route("/", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = workspace_service.get_user_workspaces(user_id)
    result = json.dumps(data, default=str)
    return Response(result, mimetype="application/json")


@api.route("/invitation", methods=['POST'])
def invite_user():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        workspace_id = request_data['workspaceId']
        invitee_email_address = request_data['inviteeEmailAddress']
        return workspace_service.invite_user(Invitation(
            _id=None,
            inviter_id=g.user_id,
            workspace_id=workspace_id,
            invitee_email_address=invitee_email_address))
    return "Workspace id and invitee email address are required"


# remember to check for permissions when we get to that part
@api.route("/user", methods=['PATCH'])
def remove_user_from_workspace():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'userId' in request_data:
        workspace_id = request_data['workspaceId']
        user_id = request_data['userId']
        return workspace_service.remove_workspace_user(workspace_id, user_id)
    return "Workspace id and user id"


@api.route("/invitation/response", methods=['POST'])
def respond_to_invitation():
    request_data = request.get_json()
    if 'invitationId' in request_data and 'accepted' in request_data:
        invitation_id = request_data['invitationId']
        accepted = request_data['accepted']
        return workspace_service.respond_to_invitation(invitation_id, accepted)
    return "Workspace id and user id"
