import pytest
import requests
import settings
import src.repository as repo

created_resources = []
base_url = "http://" + settings.APP_HOST + ":" + str(settings.APP_PORT) + "/workspaces/"

@pytest.fixture(autouse=True)
def before_test():
    details={
        'email': settings.SMTP_EMAIL_ADDRESS,
        'password': settings.SMTP_PASSWORD,
        'returnSecureToken': True
    }
    # send post request
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format("AIzaSyDAuriepQen_J7sYEo4zKZLpFnjbhljsdQ"),data=details)
    global token
    if 'idToken' in r.json().keys() :
            token = r.json()['idToken']
    yield
    for resource in created_resources:
        collection=list(resource.keys())[0]
        repo.delete(collection, kwargs={"id": resource.get(collection)})


def test_create_workspace():
    request_body={ 
        "data": {
            "workspaceName": "test workspace"
        }
    }
    response = requests.post(url = base_url, json = request_body, headers={"Authorization": token})
    assert response.status_code == 200
    created_resources.append({repo.Collection.WORKSPACE: response.content})

def test_create_workspace_fail():
    request_body_with_wrong_parameter_name={ 
        "data": {
            "workspace": "test workspace"
        }
    }
    response = requests.post(url = base_url, json = request_body_with_wrong_parameter_name, headers={"Authorization": token})
    assert response.status_code == 400

@pytest.fixture
def create_workspace_fixture():
    request_body={ 
        "data": {
            "workspaceName": "test"
        }
    }
    response = requests.post(url = base_url, json = request_body, headers={"Authorization": token})
    created_resources.append({repo.Collection.WORKSPACE: response.content})
    return response.content

def test_get_workspaces_for_user(create_workspace_fixture):
    response = requests.get(url = base_url, headers={"Authorization": token})
    assert response.status_code == 200
    assert response.content
    assert len(create_workspace_fixture) == len(response.content)
    print(create_workspace_fixture)
    print(response.content)
    assert create_workspace_fixture[0] == response.content[0]