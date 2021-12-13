from flask import Blueprint, g, request, abort, Response

from src.services import diagram_service, permission_service

api = Blueprint('diagrams_api', __name__)


# TODO: when adding roles: make sure that the creator has access and permissions to add team to the workspace
@api.route("", methods=['POST'])
def create_diagram():
    """
      Create a new diagram
      ---
      tags:
        - diagrams
      parameters:
        - in: body
          name: workspace
          schema:
            required:
              - title
              - projectId
              - path
            properties:
              title:
                type: string
              projectId:
                type: string
              path:
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
              title:
                type: string
                example: My new diagram
              projectId:
                type: str
                example: '61901338d13eab96f1e5d153'
              path:
                type: string
                example: path/of/diagram
              models:
                type: array
                items:
                  type: string
                example: ['61901488d13eab96f1e5d154']
      """
    request_data = request.get_json()
    try:
        permission_service.check_is_editor(firebase_id=g.firebase_id, project_id=request_data['projectId'])
        create_result = diagram_service.create_diagram(
            title=request_data['title'],
            projectId=request_data['projectId'],
            path=request_data['path'])
        if create_result is not None:
            return Response(create_result.as_json(), mimetype="application/json")
    except KeyError:
        abort(400, "Insufficient data in request")

