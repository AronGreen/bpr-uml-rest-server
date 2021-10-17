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
        creator_id = request_data['creatorId']
        workspace_name = request_data['workspaceName']
        return service.createWorkspace(Workspace(creator_id, workspace_name))
    return "Creator id and workspace name required"


@api.route("/", methods=['GET'])
def get_workspaces():
    user_id = g.user_id
    data = service.get_user_workspaces(user_id)
    result = json.dumps(data, default=str)
    return Response(result, mimetype="application/json")
