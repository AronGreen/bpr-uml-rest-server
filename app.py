import firebase_admin as fb_admin
from bson import json_util
from firebase_admin import auth as fb_auth
from flask import Flask, render_template, request, g, abort
from flask_cors import CORS

import src.api.users as users_api
import api.users as users_api_o
import src.api.workspace as workspaces_api
import src.services.log_service as log
import src.settings as settings
from api.teams import teams_api
from api.workspace import workspace_api
from src import repository

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(workspace_api)
app.register_blueprint(users_api_o.api)
app.register_blueprint(teams_api)
app.register_blueprint(workspaces_api.api, url_prefix='/workspaces')
app.register_blueprint(users_api.api, url_prefix='/users')

settings.ensure_firebase_config()
default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('./index.html', )


@app.route('/mate')
def mate():
    result = repository.find(repository.Collection.MATE_TEST, name2='mate')[0]
    result['name2'] = 'hellooooo'
    print(result)
    repository.update(repository.Collection.MATE_TEST, result)
    return json_util.dumps(repository.find(repository.Collection.MATE_TEST, name2='hellooooo'))


# ref: https://firebase.google.com/docs/auth/admin/manage-cookies
@app.route('/logged_in', methods=['POST'])
def session_login():
    return f"logged in as {g.user_email}"


@app.before_request
def check_auth():
    if request.path in ('/', '/mate', '/favicon.ico'):
        return
    if app.debug is True:
        g.user_email = 'debug@debug.debug'
        g.user_id = '1234'
        g.user_name = 'Mr. Debugson'
        return
    try: 
        id_token = request.headers.get('accessToken')
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


@app.errorhandler(400)
def unauthorized(error):
    return 'Bad request', 400


@app.errorhandler(401)
def unauthorized(error):
    return 'Unauthorized', 401


if __name__ == "__main__":
    app.run()
