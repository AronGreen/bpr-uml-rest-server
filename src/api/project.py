from flask import Blueprint, g, request, abort, Response
from bpr_data.models.project import Project, ProjectUser, ProjectTeam
from bpr_data.models.response import ApiResponse
from bpr_data.models.permission import WorkspacePermission
from bson import ObjectId
from src.services import permission_service, project_service
api = Blueprint('projects_api', __name__)


# TODO: when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_project():
    """
    Create a new project
    ---
    tags:
      - projects
    parameters:
      - in: body
        name: body
        schema:
          required:
            - title
            - workspaceId
          properties:
            title:
              type: string
              description: title of the project
            workspaceId:
              type: string
              description: id of the workspace
    responses:
      200:
        description: Project created
      400:
         description: Insufficient data in request
   """
    request_data = request.get_json()
    permission_service.check_permissions(firebase_id=g.firebase_id, workspace_id=ObjectId(request_data['workspaceId']),
                                         permissions=[WorkspacePermission.MANAGE_WORKSPACE])
    try:
        create_result = project_service.create_project(
            title=request_data['title'],
            workspaceId=request_data['workspaceId'],
            creator_firebase_id=g.firebase_id)
        if create_result is not None:
            return Response(create_result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")


@api.route("/<projectId>", methods=['GET'])
def get_project(projectId: str):
    """
    Get a project by id
    ---
    tags:
      - projects
    parameters:
      - in: path
        name: projectId
        required: true
    responses:
      200:
        description: project data
      404:
         description: Project not found
    """
    try:
        result = project_service.get_full_project_for_user(project_id=projectId, firebase_id=g.firebase_id)
        return Response(result.as_json(), mimetype="application/json")
    except AttributeError:
        abort(404, "Project not found")


@api.route("/<projectId>/users", methods=['POST'])
def add_users(projectId: str):
    """
    Add a user to project
    ---
    tags:
      - projects
    parameters:
      - in: body
        schema:
          properties:
            userId:
              type: string
              description: id of user to add to project
            isEditor:
              type: boolean
              description: specifies if the user will have edit access to project
    responses:
      200:
        description: User added
      400:
         description: Insufficient data in request
   """
    permission_service.check_manage_project(firebase_id=g.firebase_id, project_id=projectId)
    request_data = request.get_json()
    try:
        result = project_service.add_users(
            project_id=ObjectId(projectId),
            users=ProjectUser.to_object_ids("userId", ProjectUser.from_dict_list(request_data['users']))
        )
        return Response(result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")


@api.route("/<projectId>/users", methods=['PUT'])
def replace_users(projectId: str):
    """
    Replace all users in project
    ---
    tags:
      - projects
    parameters:
      - in: path
        name: projectId
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
                  isEditor:
                    type: string
    responses:
      200:
        description: project with updated list
      400:
         description: Insufficient data in request
   """
    permission_service.check_manage_project(firebase_id=g.firebase_id, project_id=projectId)
    request_data = request.get_json()
    try:
        result = project_service.replace_users(
            project_id=ObjectId(projectId),
            users=ProjectUser.to_object_ids("userId", ProjectUser.from_dict_list(request_data['users']))
        )
        return Response(result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")
    except AttributeError:
        abort(404, "Project not found")


@api.route("/<projectId>/teams", methods=['PUT'])
def replace_teams(projectId: str):
    """
    Replace all teams in project
    ---
    tags:
      - projects
    parameters:
      - in: path
        name: projectId
        required: true
      - in: body
        name: body
        schema:
          properties:
            teams:
              type: array
              items:
                type: object
                properties:
                  teamId:
                    type: string
                  isEditor:
                    type: boolean
    responses:
      200:
        description: project with updated list
      400:
         description: Insufficient data in request
   """
    permission_service.check_manage_project(firebase_id=g.firebase_id, project_id=projectId)
    request_data = request.get_json()
    try:
        result = project_service.replace_teams(
            project_id=ObjectId(projectId),
            teams=ProjectTeam.to_object_ids("teamId", ProjectTeam.from_dict_list(request_data['teams']))
        )
        return Response(result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")


@api.route("/<projectId>", methods=['PUT'])
def update_project_name(projectId: str):
    """
      Update a project's name
      ---
      tags:
        - projects
      parameters:
        - in: path
          name: projectId
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
          description: project
        404:
          description: project not found
      """
    permission_service.check_manage_project(firebase_id=g.firebase_id, project_id=projectId)
    request_data = request.get_json()
    if 'title' in request_data:
        title = request_data['title']
        return Response(status=200, response=Project.as_json(
            project_service.update_project_title(project_id=projectId, title=title)), mimetype="application/json")
    else:
        return Response(status=400, response=ApiResponse(response="properties missing").as_json())


@api.route("/<projectId>", methods=['DELETE'])
def delete_project(projectId: str):
    """
      Delete project
      ---
      tags:
        - projects
      parameters:
        - in: path
          name: projectId
          required: true
      responses:
        200:
          description: confirmation
      """
    permission_service.check_manage_project(firebase_id=g.firebase_id, project_id=projectId)
    return Response(status=200, response=ApiResponse(
        response=project_service.delete_project(project_id=ObjectId(projectId))).as_json(), mimetype="application/json")


@api.route("/<projectId>/user", methods=['GET'])
def get_project_user(projectId: str):
    """
      Get project user
      ---
      tags:
        - projects
      parameters:
        - in: path
          name: projectId
          required: true
      responses:
        200:
          description: user
        404:
          description: Project not found
      """
    return Response(status=200, response=project_service.get_project_user(project_id=ObjectId(projectId), firebase_id=g.firebase_id).as_json(), mimetype="application/json")