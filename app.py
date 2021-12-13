import json

import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth
from flask import Flask, render_template, request, g, abort, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from flask_swagger import swagger

import src.services.log_service as log
import settings as settings

from src.api import \
    project as project_api, \
    project_contents as project_contents_api, \
    teams as teams_api, \
    users as users_api, \
    workspace as workspace_api, \
    diagrams as diagram_api

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(project_api.api, url_prefix='/projects')
app.register_blueprint(project_contents_api.api, url_prefix='/projects/<project_id>/contents')
app.register_blueprint(teams_api.api, url_prefix='/teams')
app.register_blueprint(users_api.api, url_prefix='/users')
app.register_blueprint(workspace_api.api, url_prefix='/workspaces')
app.register_blueprint(diagram_api.api, url_prefix='/diagrams')

settings.ensure_firebase_config()
default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/swagger")
def swagger_page():
    return render_template('swagger/index.html')


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "BPR UML REST"
    return jsonify(swag)


@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        return
    if request.path in ('/', '/spec', '/swagger', '/favicon.ico') or request.path.startswith('/static'):
        return
    try:
        id_token = request.headers['Authorization'].replace('Bearer ', '')
        decoded_token = fb_auth.verify_id_token(id_token)
        g.user_email = decoded_token['email']
        g.firebase_id = decoded_token['user_id']
        # TODO: check if this is what we want
        # When logging in with email, name is not in the token
        if 'name' in decoded_token:
            g.user_name = decoded_token['name']
        else:
            g.user_name = g.user_email
    except (fb_auth.RevokedIdTokenError, fb_auth.CertificateFetchError, fb_auth.UserDisabledError,
            fb_auth.ExpiredIdTokenError) as err:
        log.log_error(err, "Authentication - expired token exception")
        abort(401)
    except (ValueError, fb_auth.InvalidIdTokenError) as err:
        log.log_error(err, "Authentication - bad token exception")
        abort(400)


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(401)
def unauthorized(error):
    return 'Unauthorized', 401


if __name__ == "__main__":
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=True)
