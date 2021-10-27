from flask import Blueprint, request, g

import src.services.users_service as service
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("/", methods=['POST'])
def add_user():
    return service.add_user(User(_id=None, user_id=g.user_id, user_name=g.user_name, email=g.user_email))


@api.route("/teams", methods=['GET'])
def get_team_for_user():
    return service.get_teams_for_user(g.user_id)
