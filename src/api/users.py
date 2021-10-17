from flask import Blueprint, request, g
import src.services.users_service as service
from src.models.invitation import Invitation
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("/invite", methods=['POST'])
def invite_user():
    request_data = request.get_json()
    if 'workspace_id' in request_data and 'invitee_email_address' in request_data:
        workspace_id = request_data['workspace_id']
        invitee_email_address = request_data['invitee_email_address']
        return service.invite_user(Invitation(g.user_name, workspace_id, invitee_email_address))
    return "Workspace id and invitee email address are required"


@api.route("/", methods=['POST'])
def add_user():
    request_data = request.get_json()
    if 'userName' in request_data:
        user_name = request_data['userName']
        return service.add_user(User(user_name))
