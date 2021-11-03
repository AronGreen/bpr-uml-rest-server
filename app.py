import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth
from flask import Flask, render_template, request, g, abort, make_response
from flask_cors import CORS

import src.services.log_service as log
import src.settings as settings

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


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        _build_cors_preflight_response()
    if request.path in ('/', '/mate', '/favicon.ico'):
        return
    if app.debug is True:
        g.user_email = 'debug@debug.debug'
        g.user_id = '1234'
        g.user_name = 'Mr. Debugson'
        return
    try: 
        id_token = request.headers['Authorization'].replace('Bearer ', '')
        decoded_token = fb_auth.verify_id_token(id_token)
        g.user_email = decoded_token['email']
        g.user_id = decoded_token['user_id']
        g.user_name = decoded_token['name']
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
    app.run()
