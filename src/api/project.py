from flask import Blueprint, g, request, abort, Response

from src.services import project_service

api = Blueprint('projects_api', __name__)


# TODO: when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_project():
    request_data = request.get_json()
    try:
        create_result = project_service.create_project(
            title=request_data['title'],
            workspaceId=request_data['workspaceId'],
            creator_firebase_id=g.firebase_id)
        if create_result is not None:
            return Response(create_result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")


@api.route("/<projectId>/user", methods=['POST'])
def add_user(projectId: str):
    request_data = request.get_json()
    try:
        result = project_service.add_user(
            project_id=projectId,
            user_id=request_data['userId'],
            is_editor=request_data['isEditor'])
        return Response({'success': result}, mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request body")

