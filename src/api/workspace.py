from bson import ObjectId
from flask import Blueprint, request, g, abort
from flask.wrappers import Response

from bpr_data.models.invitation import Invitation
from bpr_data.models.user import User
from bpr_data.models.team import Team
from bpr_data.models.workspace import Workspace
from bpr_data.models.response import ApiResponse

from src.services import workspace_service, users_service, project_service

api = Blueprint('workspace_api', __name__)


@api.route("", methods=['POST'])
def create_workspace():
    """
      Create a new workspace
      ---
      tags:
        - workspaces
      parameters:
        - in: body
          name: workspace
          schema:
            required:
              - name
            properties:
              name:
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
              name:
                type: string
                example: AwesomeCO's workspace
              users:
                type: array
                items:
                  type: string
                example: ['61901488d13eab96f1e5d154']
      """
    request_data = request.get_json()
    if 'name' in request_data:
        to_create = Workspace(
            _id=None,
            name=request_data['name'],
            users=list())
        created = workspace_service.create_workspace(to_create)
        return Response(created.as_json(), mimetype="application/json")
    abort(400, description="Workspace name needed")


@api.route("", methods=['GET'])
def get_workspaces():
    """
      Get all workspaces for current user.
      ---
      tags:
        - workspaces
      responses:
        200:
          description: list with results
          schema:
            type: array
            items:
              type: object
              properties:
                _id:
                  type: str
                  example: '61901338d13eab96f1e5d153'
                name:
                  type: string
                  example: AwesomeCO's workspace
                users:
                  type: array
                  items:
                    type: string
                  example: ['61901488d13eab96f1e5d154']
      """
    firebase_id = g.firebase_id
    data = workspace_service.get_user_workspaces(firebase_id)
    result = Workspace.as_json_list(data)
    return Response(result, mimetype="application/json")


@api.route("/<workspaceId>", methods=['GET'])
def get_workspace(workspaceId: str):
    """
      Get workspace by workspace id.
      ---
      tags:
        - workspaces
      parameters:
        - in: path
          name: workspaceId
          required: true
      responses:
        200:
          description: workspace object
          schema:
            type: object
            properties:
              _id:
                type: str
                example: '61901338d13eab96f1e5d153'
              name:
                type: string
                example: AwesomeCO's workspace
              users:
                type: array
                items:
                  type: string
                example: ['61901488d13eab96f1e5d154']
      """
    result = workspace_service.get_workspace(ObjectId(workspaceId))
    return Response(result.as_json(), mimetype="application/json")


@api.route("/<workspaceId>/users", methods=['GET'])
def get_workspace_users(workspaceId: str):
    """
      Get workspace users by workspace id.
      ---
      tags:
        - workspaces
      parameters:
        - in: path
          name: workspaceId
          required: true
      responses:
        200:
          description: A JSON array of users
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
                example: kejflksjæakdfæk
      """
    result = workspace_service.get_workspace_users(workspaceId)
    return Response(User.as_json_list(result), mimetype="application/json")


@api.route("/<workspaceId>/projects", methods=['GET'])
def get_workspace_user_projects(workspaceId: str):
    """
      Get projects for current user and workspace
      ---
      tags:
        - workspaces
        - projects
      parameters:
        - in: path
          name: workspaceId
          required: true
      responses:
        200:
          description: A JSON array of projects
          schema:
            type: object
            properties:
              _id:
                type: str
                example: '61901338d13eab96f1e5d153'
              title:
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
              teams:
                type: array
                items:
                  type: object
                  properties:
                    teamId:
                      type: str
                      example: '61901338d13eab96f1e5d153'
                    isEditor:
                      type: boolean
      """
    user_id = users_service.get_user_by_firebase_id(g.firebase_id).id
    result = project_service.get_user_projects(workspaceId, user_id)
    return Response(User.as_json_list(result), mimetype="application/json")


@api.route("/invitation", methods=['POST'])
def invite_user():
    """
      Start invitation flow for user
      ---
      tags:
        - workspaces
        - users
        - invitations
      parameters:
        - in: body
          name: invitation
          schema:
            required:
              - workspaceId
              - inviteeEmailAddress
            properties:
              workspaceId:
                type: string
              inviteeEmailAddress:
                type: string
      responses:
        200:
          description: Invitation flow is started for user
      """
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'inviteeEmailAddress' in request_data:
        invitation = Invitation(
            _id=None,
            inviterId=g.firebase_id,
            workspaceId=ObjectId(request_data['workspaceId']),
            inviteeEmailAddress=request_data['inviteeEmailAddress'])
        result = workspace_service.invite_user(invitation)
        return Response(result.as_json(), status=200, mimetype="application/json")
    return Response("Workspace id and invitee email address are required", mimetype="application/json")


# TODO: remember to check for permissions when we get to that part
@api.route("/user", methods=['DELETE'])
def remove_user_from_workspace():
    """
      Remove user from workspace
      ---
      tags:
        - workspaces
        - users
      parameters:
        - in: body
          name: body
          schema:
            required:
              - workspaceId
              - userId
            properties:
              workspaceId:
                type: string
              userId:
                type: string
      responses:
        200:
          description: User is removed
      """
    request_data = request.get_json()
    if 'workspaceId' in request_data and 'userId' in request_data:
        if workspace_service.remove_workspace_user(
                request_data['workspaceId'],
                request_data['userId']):
            return Response(status=200)
        else:
            abort(500, description="Something went wrong")
    return abort(400, descriptioin="Workspace id and/or user id missing")


@api.route("/invitation/response", methods=['POST'])
def respond_to_invitation():
    """
      Respond to invitation
      ---
      tags:
        - workspaces
        - invitations
      parameters:
        - in: body
          name: body
          schema:
            required:
              - invitationId
              - accepted
            properties:
              invitationId:
                type: string
              accepted:
                type: boolean
      responses:
        200:
          description: User is removed
      """
    request_data = request.get_json()
    if 'invitationId' in request_data and 'accepted' in request_data:
        invitation_id = request_data['invitationId']
        accepted = request_data['accepted']
        return Response(status=200, response=ApiResponse(response=workspace_service.respond_to_invitation(invitation_id, accepted)))
    return Response(status=400, response=ApiResponse(response="Insufficient data").as_json())

@api.route("/<workspaceId>/teams", methods=['GET'])
def get_workspace_team(workspaceId: str):
    """
      Get the teams inside a workspace
      ---
      tags:
        - workspaces
      parameters:
        - in: path
          name: workspaceId
          required: true
      responses:
        200:
          description: teams
        404:
          description: workspace not found
      """
    return Response(status=200, response=Team.as_json_list(workspace_service.get_teams(workspaceId)), mimetype="application/json")
