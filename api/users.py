from flask import Blueprint, request, g
import services.users.usersService as service
from models.invitation import Invitation
from models.user import User

users_api = Blueprint('users_api', __name__)

@users_api.route("/invitation", methods=['POST'])
def inviteUser():
    request_data = request.get_json()
    if 'workspace_id' in request_data and 'invitee_email_address' in request_data:
        workspace_id = request_data['workspace_id']
        invitee_emailAddress = request_data['invitee_email_address']
        return service.inviteUser(Invitation(g.user_name, workspace_id, invitee_emailAddress))
    return "Workspace id and invitee email address are required"

@users_api.route("/user", methods=['POST'])
def addUser():
    return service.addUser(User(g.user_name, g.user_email, g.user_id))
