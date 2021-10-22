from flask import Blueprint, request, g
import json
from models.invitation import Invitation
from flask.wrappers import Response
from models.workspace import Workspace
import services.workspaces.workspacesService as service

workspace_api = Blueprint('workspace_api', __name__)

@workspace_api.route("/workspace", methods=['POST'])
def createWorkspace():
    request_data = request.get_json()
    if 'workspaceName' in request_data:
        workspace_name = request_data['workspaceName']
        return service.createWorkspace(Workspace(g.user_id, workspace_name))
    return "Workspace name required"


@workspace_api.route("/workspaces", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = service.get_user_workspaces(user_id)
    result = json.dumps(data, default=str)
    return Response(result, mimetype="application/json")
     
@workspace_api.route("/workspace/invitation", methods=['POST'])
def inviteUser():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        workspace_id = request_data['workspaceId']
        invitee_email_address = request_data['inviteeEmailAddress']
        return service.inviteUser(Invitation(g.user_id, workspace_id, invitee_email_address))
    return "Workspace id and invitee email address are required"

#remember to check for permissions when we get to that part
@workspace_api.route("/workspace/user", methods=['PATCH'])
def remove_user_from_workspace():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'userId' in request_data:
        workspace_id = request_data['workspaceId']
        user_id = request_data['userId']
        return service.remove_user_from_workspace(user_id, workspace_id)
    return "Workspace id and user id"

@workspace_api.route("/workspace/invitation/response", methods=['POST'])
def respond_to_invitation():
    request_data = request.get_json()
    if 'invitationId' in request_data and 'accepted' in request_data:
        invitation_id = request_data['invitationId']
        accepted = request_data['accepted']
        return service.respond_to_invitation(invitation_id, accepted)
    return "Workspace id and user id"