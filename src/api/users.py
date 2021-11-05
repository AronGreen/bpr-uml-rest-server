from flask import Blueprint, request, g, Response, abort

from src.services import users_service
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("/", methods=['POST'])
def add_user():
    try:
        user = User(
            _id=None,
            firebaseId=g.user_id,
            name=g.user_name,
            email=g.user_email)
        created = users_service.add_user(user)
        if created is not None:
            return Response(created.as_json(), mimetype="application/json")
        else:
            return Response('{}', mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")


@api.route("/teams", methods=['GET'])
def get_team_for_user():
    find_result = users_service.get_teams_for_user(g.user_id)
    return Response(User.as_json_list(find_result), mimetype="application/json")
