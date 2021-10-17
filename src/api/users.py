from flask import Blueprint, request
import services.users.usersService as service
from models.invitation import Invitation
from models.user import User

api = Blueprint('users_api', __name__)


@api.route("/invite", methods=['POST'])
def invite_user():
    request_data = request.get_json()
    if 'invitorId' in request_data and 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        invitor_id = request_data['invitorId']
        workspace_id = request_data['workspaceId']
        invitee_email_address = request_data['inviteeEmailAddress']
        return service.inviteUser(Invitation(invitor_id, workspace_id, invitee_email_address))
    return "Invitor id, workspace id and invitee email address are required"


@api.route("/", methods=['POST'])
def add_user():
    request_data = request.get_json()
    if 'userName' in request_data:
        user_name = request_data['userName']
        return service.addUser(User(user_name))
