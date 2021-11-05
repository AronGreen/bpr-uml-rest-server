import settings
import requests
import src.repository as repo

def cleanup(resources: list):
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