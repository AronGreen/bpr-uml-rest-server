from flask import Blueprint, request
import services.users.usersService as service
from models.invitation import Invitation
from models.user import User

users_api = Blueprint('users_api', __name__)

@users_api.route("/users/invite", methods=['POST'])
def inviteUser():
    request_data = request.get_json()
    if 'invitorId' in request_data and 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        invitorId = request_data['invitorId']
        workspaceId = request_data['workspaceId']
        inviteeEmailAddress = request_data['inviteeEmailAddress']
        return service.inviteUser(Invitation(invitorId, workspaceId, inviteeEmailAddress))
    return "Invitor id, workspace id and invitee email address are required"

@users_api.route("/users", methods=['POST'])
def addUser():
    request_data = request.get_json()
    if 'userName' in request_data:
        userName = request_data['userName']
        return service.addUser(User(userName))
