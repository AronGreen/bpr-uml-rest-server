from flask import Blueprint, g, request, abort, Response

from src.services import project_service
from src.models.project import Project

api = Blueprint('projects_api', __name__)


# TODO: when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("/", methods=['POST'])
def create_project():
    request_data = request.get_json()
    try:
        if '_id' not in request_data:
            request_data['_id'] = None
        project = Project.from_dict(request_data)
        create_result = project_service.create_project(project)
        if create_result is not None:
            return Response(create_result.as_json(), mimetype="application/json")
    except Exception as err:
        abort(403, err.__repr__())

