import settings
import requests
import src.repository as repo
from src.models.user import User

port_no = str(settings.APP_PORT)
# port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/"

created_resources = []


def cleanup(resources: list):
    resources.extend(created_resources)
    for resource in resources:
        collection = list(resource.keys())[0]
        repo.delete(collection, _id=resource.get(collection))


def get_token():
    details = {
        'email': settings.SMTP_EMAIL_ADDRESS,
        'password': settings.SMTP_PASSWORD,
        'returnSecureToken': True
    }
    # send post request
    r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(
        "AIzaSyDAuriepQen_J7sYEo4zKZLpFnjbhljsdQ"), data=details)
    if 'idToken' in r.json().keys():
        return r.json()['idToken']


def create_user(token: str):
    response = requests.post(url=base_url + "users", headers={"Authorization": token})
    result = User.from_json(response.content.decode())
    created_resources.append({repo.Collection.USER: result._id})
    return result
