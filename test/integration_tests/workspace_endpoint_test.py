import pytest
import json
import requests
import settings
import src.repository as repo
from src.models.workspace import Workspace

created_resources = []
port_no = str(settings.APP_PORT)
port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/workspaces/"


@pytest.fixture(autouse=True)
def before_test():
    details = {
        'email': settings.SMTP_EMAIL_ADDRESS,
        'password': settings.SMTP_PASSWORD,
        'returnSecureToken': True
    }
    # send post request
    r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(
        "AIzaSyDAuriepQen_J7sYEo4zKZLpFnjbhljsdQ"), data=details)
    global token
    if 'idToken' in r.json().keys():
        token = r.json()['idToken']
    yield
    for resource in created_resources:
        collection = list(resource.keys())[0]
        repo.delete(collection, id=resource.get(collection))


@pytest.fixture
def create_workspace_fixture():
    request_body = {
        "workspaceName": "test workspace"
    }
    response = requests.post(url=base_url, json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    created_resources.append({repo.Collection.WORKSPACE: workspace._id})
    return workspace


def test_get_workspaces_for_user(create_workspace_fixture):
    response = requests.get(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json_list(response.content.decode())
    assert len(result) == 1
    assert str(result[0]._id) == create_workspace_fixture._id
    assert str(result[0].workspace_name) == create_workspace_fixture.workspace_name


def test_create_workspace():
    request_body = {
        "workspaceName": "new test workspace"
    }
    response = requests.post(url=base_url, json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    created_resources.append({repo.Collection.WORKSPACE: Workspace.from_dict(response.content.decode())._id})


def test_create_workspace_fail():
    request_body_with_wrong_parameter_name = {
        "workspace": "test workspace"
    }
    response = requests.post(url=base_url, json=request_body_with_wrong_parameter_name,
                             headers={"Authorization": token})
    assert response.status_code == 400
