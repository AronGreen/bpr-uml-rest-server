from flask import Blueprint, request
from models.workspace import Workspace
import services.workspaces.workspacesService as service

workspace_api = Blueprint('workspace_api', __name__)

@workspace_api.route("/workspace", methods=['POST'])
def createWorkspace():
    request_data = request.get_json()
    if 'creatorId' in request_data and 'workspaceName' in request_data:
        creatorId = request_data['creatorId']
        workspaceName = request_data['workspaceName']
        return service.createWorkspace(Workspace(creatorId, workspaceName))
    return "Creator id and workspace name required"


@workspace_api.route("/test", methods=['GET'])
def test():
    return "Testy test"