from flask import Blueprint, g
import services.users.usersService as service
from models.user import User

users_api = Blueprint('users_api', __name__)

@users_api.route("/user", methods=['POST'])
def addUser():
    return service.addUser(User(g.user_name, g.user_email, g.user_id))
