from flask import Blueprint, g, request
from services import teamsService as service
from models.team import Team

teams_api = Blueprint('teams_api', __name__)

#when adding roles: make sure that the creator has access and permissions to add team to the workspace
@teams_api.route("/team", methods=['POST'])
def create_team():
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'teamName' in request_data:
        workspace_id = request_data['workspaceId']
        team_name = request_data['teamName']
        return service.create_team(Team(team_name, workspace_id))
    return "Workspace name required"
    
@teams_api.route("/team/users", methods=['POST'])
def update_users():
    request_data = request.get_json()
    if 'teamId' in request_data and 'users' in request_data:
        team_id = request_data['teamId']
        users = request_data['users']
        return service.update_users(team_id, users)
    return "Workspace name required"
