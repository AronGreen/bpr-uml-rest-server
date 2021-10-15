from bson.objectid import ObjectId
from flask import Flask, render_template, request, g, abort
from flask_cors import CORS

import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth

from services.log_service import log_error
from api.users import users_api
from api.workspace import workspace_api
import settings
from src import repository
import json
from bson import json_util

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(workspace_api)
app.register_blueprint(users_api)

settings.ensure_firebase_config()
default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('./index.html',)

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
    try: 
        id_token = request.json['idToken']
        decoded_token = fb_auth.verify_id_token(id_token)
        g.user_email = decoded_token['email']
        g.user_id = decoded_token['user_id']
    except (fb_auth.RevokedIdTokenError, fb_auth.CertificateFetchError, fb_auth.UserDisabledError, fb_auth.ExpiredIdTokenError) as err:
        log_error(err, "Authentication - expired token exception")
        abort(401)
    except (ValueError, fb_auth.InvalidIdTokenError) as err:
        log_error(err, "Authentication - bad token exception")
        abort(400)
  


@app.errorhandler(400)
def unauthorized(error):
    return ('Bad request', 400)


@app.errorhandler(401)
def unauthorized(error):
    return ('Unauthorized', 401)


if __name__ == "__main__":
    app.run()