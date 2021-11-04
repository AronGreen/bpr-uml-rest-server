import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth
from flask import Flask, render_template, request, g, abort, make_response
from flask_cors import CORS

import src.services.log_service as log
import settings as settings

import src.api.project as project_api
import src.api.teams as teams_api
import src.api.users as users_api
import src.api.workspace as workspace_api

app = Flask(__name__)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(project_api.api, url_prefix='/projects')
app.register_blueprint(teams_api.api, url_prefix='/teams')
app.register_blueprint(users_api.api, url_prefix='/users')
app.register_blueprint(workspace_api.api, url_prefix='/workspaces')

settings.ensure_firebase_config()
default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('index.html')


# def _build_cors_preflight_response():
#     response = make_response()
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add("Access-Control-Allow-Headers", "*")
#     response.headers.add("Access-Control-Allow-Methods", "*")
#     return response


@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        return
    if request.path in ('/', '/mate', '/favicon.ico'):
        return
    try:
        id_token = request.headers['Authorization'].replace('Bearer ', '')
        decoded_token = fb_auth.verify_id_token(id_token)
        g.user_email = decoded_token['email']
        g.user_id = decoded_token['user_id']
        # TODO: check if this is what we want
        # When logging in with email, name is not in the token
        if 'name' in decoded_token:
            g.user_name = decoded_token['name']
        else:
            g.user_name = g.user_email
    except (fb_auth.RevokedIdTokenError, fb_auth.CertificateFetchError, fb_auth.UserDisabledError, fb_auth.ExpiredIdTokenError) as err:
        log.log_error(err, "Authentication - expired token exception")
        abort(401)
    except (ValueError, fb_auth.InvalidIdTokenError) as err:
        log.log_error(err, "Authentication - bad token exception")
        abort(400)


# TODO: add more errorhandlers
@app.errorhandler(400)
def unauthorized(error):
    return 'Bad request', 400


@app.errorhandler(401)
def unauthorized(error):
    return 'Unauthorized', 401


if __name__ == "__main__":
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=True)
