from flask import Blueprint, request, abort, Response
from bson import ObjectId

from bpr_data.models.team import Team, TeamUser
from bpr_data.models.response import ApiResponse

from src.services import teams_service as service

api = Blueprint('teams_api', __name__)


# when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_team():
    """
      Create a new team
      ---
      tags:
        - teams
      parameters:
        - in: body
          name: team
          schema:
            required:
              - workspaceId
              - teamName
            properties:
              workspaceId:
                type: string
              teamName:
                type: string
      responses:
        200:
          description: User created
          schema:
            type: object
            properties:
              _id:
                type: str
                example: '61901338d13eab96f1e5d153'
              workspaceId:
                type: str
                example: '61901338d13eab96f1e5d153'
              name:
                type: string
              users:
                type: array
                items:
                  type: string
                example: ['61901488d13eab96f1e5d154']
      """
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'name' in request_data:
        workspaceId = request_data['workspaceId']
        name = request_data['name']
        created = service.create_team(Team(_id=None, workspaceId=ObjectId(workspaceId), name=name, users=[]))
        if created is not None:
            return Response(created.as_json(), mimetype="application/json")
        else:
            return Response('{}', mimetype="application/json")
    return ApiResponse(response="properties missing").as_json()


@api.route("/users", methods=['POST'])
def add_users():
    """
      Add users to team
      ---
      tags:
        - teams
      parameters:
        - in: body
          name: body
          schema:
            properties:
              teamId:
                type: string
                example: '61901338d13eab96f1e5d153'
              userIds:
                type: array
                items:
                  type: string
                  example: '61901338d13eab96f1e5d153'
      responses:
        200:
          description: User created
          schema:
            type: object
      """
    request_data = request.get_json()
    if 'teamId' in request_data and 'users' in request_data:
        team_id = request_data['teamId']
        result = service.add_users(team_id, TeamUser.to_object_ids("userId", TeamUser.from_json_list(request_data['users'])))
        return Response(result.as_json(), mimetype="application/json")
    abort(400)

@api.route("/<teamId>/users", methods=['PUT'])
def replace_users(teamId):
    """
      Replace the users of team
      ---
      tags:
        - teams
      parameters:
        - in: path
          name: teamId
          required: true
        - in: body
          name: body
        schema:
          properties:
            users:
              type: array
              items:
                type: object
                properties:
                  userId:
                    type: string
      responses:
        200:
          description: Users updated
          schema:
            type: object
        404:
          description: Team not found
      """
    request_data = request.get_json()
    result = service.replace_users(teamId, TeamUser.to_object_ids("userId", TeamUser.from_json_list(request_data['users'])))
    return Response(result.as_json(), mimetype="application/json")

@api.route("/users", methods=['DELETE'])
def remove_user():
    """
      Remove users from team
      ---
      tags:
        - teams
      parameters:
        - in: body
          name: body
          schema:
            properties:
              teamId:
                type: string
                example: '61901338d13eab96f1e5d153'
              userIds:
                type: array
                items:
                  type: string
                  example: '61901338d13eab96f1e5d153'
      responses:
        200:
          description: User created
          schema:
            type: object
      """
    request_data = request.get_json()
    if 'teamId' in request_data and 'userIds' in request_data:
        team_id = request_data['teamId']
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.remove_user(team_id, user_id)
        return Response('{}', mimetype="application/json")
    abort(400)
