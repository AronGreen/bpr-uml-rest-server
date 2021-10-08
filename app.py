from logging import error
from flask import Flask, render_template, request
from api.workspace import workspace_api
import settings
import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth
from flask_cors import CORS, cross_origin
# TODO: create logging service
import mongo as db

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(workspace_api)

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
        db.debug_log(uid, 'token from login')
        return f"logged in with id {uid}"
        # TODO: use @app.errorhandler
    except Exception as err:
        db.debug_log(err, 'error on login')
        return "something bad happened, check debug log"


if __name__ == "__main__":
    app.run()