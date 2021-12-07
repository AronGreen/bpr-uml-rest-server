import json

from flask import Blueprint, request, Response, abort

from src.services import project_contents_service

api = Blueprint('projects_contents_api', __name__)


@api.route("", methods=['GET'])
def get_project_contents(project_id):
    """
      Get project contents
      ---
      tags:
        - projects
        - project/contents
      parameters:
        - in: path
          name: projectId
          required: true
      responses:
        200:
          description: object containing list of project items
    """
    return project_contents_service.get_project_contents(project_id=project_id)


@api.route("", methods=['POST'])
def add_folder(project_id):
    """
      Add a folder to a project
      ---
      tags:
        - projects
        - project/contents
      parameters:
        - in: path
          required: true
        - in: body
          schema:
            required:
              - folder
            properties:
              folder:
                type: string
      responses:
        200:
          description: success true/false
    """
    request_data = request.get_json()
    try:
        result = project_contents_service.create_folder(
            projectId=project_id,
            path=request_data['folder'])
        return Response(json.dumps({'success': result}), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")


@api.route("", methods=['DELETE'])
def delete_folder(project_id):
    """
    Try to remove a folder from a project.
    Only empty folders or folders with empty subfolders can be deleted
    ---
    tags:
      - projects
      - project/contents
    parameters:
      - in: path
        required: true
      - in: body
        schema:
          required:
            - folder
          properties:
            folder:
              type: string
    responses:
      200:
        description: success true/false
    """
    request_data = request.get_json()
    try:
        result = project_contents_service.delete_folder(
            project_id=project_id,
            path=request_data['folder'])
        return Response(json.dumps({'success': result}), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")
