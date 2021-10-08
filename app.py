from flask import Flask, render_template, request
from api.workspace import workspace_api
from api.users import users_api
import settings
import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth
from flask_cors import CORS, cross_origin

from api.workspace import workspace_api
from services.log_service import log_debug, log_error
import settings

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(workspace_api)
app.register_blueprint(users_api)

settings.ensure_firebase_config()
default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('./index.html',)


# ref: https://firebase.google.com/docs/auth/admin/manage-cookies
@app.route('/logged_in', methods=['POST'])
@cross_origin()
def session_login():
    try:
        id_token = request.json['idToken']
        decoded_token = fb_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        log_debug(decoded_token, 'token from login')
        return f"logged in with id {uid}"
        # TODO: use @app.errorhandler
    except Exception as err:
        log_error(err, 'error on login')
        return "something bad happened, check error log"


if __name__ == "__main__":
    app.run()