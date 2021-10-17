from flask import Blueprint, request, g
import json

from flask.wrappers import Response
from models.workspace import Workspace
import services.workspaces.workspacesService as service

api = Blueprint('workspace_api', __name__)


@api.route("/", methods=['POST'])
def create_workspace():
    request_data = request.get_json()
    if 'creatorId' in request_data and 'workspaceName' in request_data:
        workspace_name = request_data['workspaceName']
        return service.createWorkspace(Workspace(g.user_id, workspace_name))
    return "Workspace name required"


@api.route("/", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = service.get_user_workspaces(user_id)
    result = json.dumps(data, default=str)
    return Response(result, mimetype="application/json")
