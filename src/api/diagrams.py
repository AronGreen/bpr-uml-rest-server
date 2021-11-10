from flask import Blueprint, g, request, abort, Response

from src.services import diagram_service

api = Blueprint('diagrams_api', __name__)


# TODO: when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_diagram():
    request_data = request.get_json()
    try:
        create_result = diagram_service.create_diagram(
            title=request_data['title'],
            projectId=request_data['projectId'],
            path=request_data['path'])
        if create_result is not None:
            return Response(create_result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")

