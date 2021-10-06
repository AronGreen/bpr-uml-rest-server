from flask import Blueprint, request
import services.workspaces.workspacesService as service

workspace_api = Blueprint('workspace_api', __name__)

@workspace_api.route("/workspace", methods=['POST'])
def createWorkspace():
    request_data = request.get_json()
    if 'creatorId' in request_data and 'workspaceName' in request_data:
        return service.createWorkspace(request_data)
    return "Creator id and workspace name required"


@workspace_api.route("/test", methods=['GET'])
def test():
    return "Testy test"