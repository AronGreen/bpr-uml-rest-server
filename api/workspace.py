from flask import Blueprint, request, g
import json

from flask.wrappers import Response
from models.workspace import Workspace
import services.workspaces.workspacesService as service

workspace_api = Blueprint('workspace_api', __name__)

@workspace_api.route("/workspace", methods=['POST'])
def createWorkspace():
    request_data = request.get_json()
    if 'workspace_name' in request_data:
        workspace_name = request_data['workspace_name']
        return service.createWorkspace(Workspace(g.user_id, workspace_name))
    return "Workspace name required"


@workspace_api.route("/workspaces", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = service.get_user_workspaces(user_id)
    result = json.dumps(data, default=str)
    return Response(result, mimetype="application/json")
     


