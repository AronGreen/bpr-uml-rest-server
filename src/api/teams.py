from flask import Blueprint, request, abort, Response, g
from bson import ObjectId

from bpr_data.models.team import Team, TeamUser
from bpr_data.models.response import ApiResponse

from src.services import teams_service as service
from bpr_data.models.permission import WorkspacePermission
import src.services.permission_service as permission_service

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
    permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(request_data['workspaceId']), permissions=[WorkspacePermission.MANAGE_TEAMS])
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
        team=service.get_team(team_id=ObjectId(team_id))
        permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(team.workspaceId), permissions=[WorkspacePermission.MANAGE_TEAMS])
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
    team=service.get_team(team_id=ObjectId(teamId))
    permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(team.workspaceId), permissions=[WorkspacePermission.MANAGE_TEAMS])
    result = service.replace_users(teamId, TeamUser.to_object_ids("userId", TeamUser.from_dict_list(request_data['users'])))
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
        team=service.get_team(team_id=team_id)
        permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(team.workspaceId), permissions=[WorkspacePermission.MANAGE_TEAMS])
        user_ids = request_data['userIds']
        for user_id in user_ids:
            service.remove_user(team_id, user_id)
        return Response('{}', mimetype="application/json")
    abort(400)

@api.route("/<teamId>", methods=['GET'])
def get_team_by_team_id(teamId: str):
    """
      Get team by team id
      ---
      tags:
        - teams
      parameters:
        - in: path
          name: teamId
          required: true
      responses:
        200:
          description: User created
          schema:
            type: object
      """
    result = service.get_team_with_user_details_for_user(team_id = ObjectId(teamId), firebase_id=g.firebase_id)
    return Response(result.as_json(), mimetype="application/json")

@api.route("/<teamId>", methods=['PUT'])
def update_team_name(teamId: str):
    """
      Update a team's name
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
            required:
              - name
            properties:
              name:
                type: string
      responses:
        200:
          description: teams
        404:
          description: team not found
      """
    team=service.get_team(team_id=ObjectId(teamId))
    permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(team.workspaceId), permissions=[WorkspacePermission.MANAGE_TEAMS])
    request_data = request.get_json()
    if 'name' in request_data:
        name = request_data['name']
    return Response(status=200, response=Team.as_json(service.update_team_name(team_id=ObjectId(teamId), name=name)), mimetype="application/json")

@api.route("/<teamId>", methods=['DELETE'])
def delete_team(teamId: str):
  """
      Delete team
      ---
      tags:
        - teams
      parameters:
        - in: path
          name: teamId
          required: true
      responses:
        200:
          description: confirmation
      """
  team=service.get_team(team_id=ObjectId(teamId))
  permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(team.workspaceId), permissions=[WorkspacePermission.MANAGE_TEAMS])
  return Response(status=200, response=ApiResponse(service.delete_team(team_id=ObjectId(teamId))).as_json(), mimetype="application/json")