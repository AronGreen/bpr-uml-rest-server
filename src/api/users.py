from flask import Blueprint, request, g, Response

import src.services.users_service as service
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("/", methods=['POST'])
def add_user():
    user = User(_id=None, userId=g.user_id, name=g.user_name, email=g.user_email)
    created = service.add_user(user)
    if created is not None:
        return Response(created.as_json(), mimetype="application/json")
    else:
        return Response('{}', mimetype="application/json")


@api.route("/teams", methods=['GET'])
def get_team_for_user():
    find_result = service.get_teams_for_user(g.user_id)
    return Response(User.as_json_list(find_result), mimetype="application/json")
