from flask import Flask, render_template, request
from api.workspace import workspace_api
import settings
import firebase_admin as fb_admin
from firebase_admin import auth as fb_auth


app = Flask(__name__)

app.register_blueprint(workspace_api)

default_app = fb_admin.initialize_app()


@app.route("/")
def index():
    return render_template('./index.html',)


# ref: https://firebase.google.com/docs/auth/admin/manage-cookies
@app.route('/logged_in', methods=['GET'])
def session_login():
    try:
        id_token = request.json['idToken']
        decoded_token = fb_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return f"logged in with id {uid}"
        # TODO: use @app.errorhandler
    except:
        return "something bad happened"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5080)