from flask import Blueprint, g, Response, abort
from src.models.invitation import Invitation

from src.services import users_service
from src.services import invitation_service
from src.models.user import User

api = Blueprint('users_api', __name__)


@api.route("", methods=['POST'])
def ensure_user_exists():
    """
      Ensures a user exists in our database.
      ---
      tags:
        - users
      responses:
        200:
          description: User definitely exists
          schema:
            type: object
            properties:
              _id:
                type: str
                example: '61901338d13eab96f1e5d153'
              name:
                type: string
                example: John Doe
              email:
                type: string
                example: j.doe@example.com
              firebaseId:
                type: string
                example: asdfagawreg
      """
    try:
        user = users_service.get_user_by_firebase_id(g.firebase_id)
        if user is not None:
            return Response(user.as_json(), mimetype="application/json")

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
def get_teams_for_user():
    """
      Get teams for current user
      ---
      tags:
        - users
        - teams
      responses:
        200:
          description: A JSON array of projects
          schema:
            type: object
            properties:
              _id:
                type: str
                example: '61901338d13eab96f1e5d153'
              workspaceId:
                type: str
                example: '61901338d13eab96f1e5d153'
              teamName:
                type: string
                example: AwesomeCO's workspace
              users:
                type: array
                items:
                  type: object
                  properties:
                    userId:
                      type: str
                      example: '61901338d13eab96f1e5d153'
                    isEditor:
                      type: boolean
      """
    find_result = users_service.get_teams_for_user(g.firebase_id)
    return Response(User.as_json_list(find_result), mimetype="application/json")


@api.route("/invitations", methods=['GET'])
def get_workspace_invitations_for_user():
    """
      Get workspace invitations for current user
      ---
      tags:
        - users
      responses:
        200:
          description: A JSON array of projects
          schema:
            type: array
            items:
              type: object
              properties:
                _id:
                  type: str
                  example: '61901338d13eab96f1e5d153'
                inviterId:
                  type: str
                  example: '61901338d13eab96f1e5d153'
                workspaceId:
                  type: str
                  example: '61901338d13eab96f1e5d153'
                inviteeEmailAddress:
                  type: string
                  example: j.doe@example.com
      """
    find_result = invitation_service.get_workspace_invitations_for_user(g.user_email)
    return Response(Invitation.as_json_list(find_result), mimetype="application/json")
