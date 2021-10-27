from flask import Blueprint, g
import services.users.usersService as service
from models.user import User

api = Blueprint('users_api', __name__)


@api.route("/user", methods=['POST'])
def addUser():
    return service.addUser(User(g.user_name, g.user_email, g.user_id))


@api.route("/user/teams", methods=['GET'])
def get_team_for_user():
    return service.get_teams_for_user(g.user_id)
