from flask import Blueprint, request, g, Response, abort

from src.services import users_service
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("/", methods=['POST'])
def add_user():
    try:
        user = users_service.get_user_by_firebase_id(g.firebase_id)
        if user is not None:
            abort(400, description="User already exists")

        user = users_service.add_user(User(
            _id=None,
            firebaseId=g.firebase_id,
            name=g.user_name,
            email=g.user_email))
        if user is not None:
            return Response(user.as_json(), mimetype="application/json")
        else:
            return Response('{}', mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")


@api.route("/teams", methods=['GET'])
def get_team_for_user():
    find_result = users_service.get_teams_for_user(g.firebase_id)
    return Response(User.as_json_list(find_result), mimetype="application/json")
