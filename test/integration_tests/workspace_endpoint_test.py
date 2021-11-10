import pytest
import requests
import settings
import src.repository as repo
from src.models.workspace import Workspace
from src.models.user import User
import src.services.invitation_service
import endpoint_test_util as util
import json

created_resources = []
port_no = str(settings.APP_PORT)
# port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/"


@pytest.fixture(autouse=True)
def before_test():
    global token
    global user
    token = util.get_token()
    user = util.create_user(token)
    yield
    util.cleanup(created_resources)


@pytest.fixture
def create_workspace_fixture() -> Workspace:
    request_body = {
        "name": "test workspace"
    }
    response = requests.post(url=base_url + "workspaces", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    created_resources.append({repo.Collection.WORKSPACE: workspace.id})
    return workspace


def test_get_workspaces_for_user(create_workspace_fixture):
    response = requests.get(url=base_url + "workspaces", headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json_list(response.content.decode())
    print(result)
    assert len(result) == 1
    assert str(result[0]._id) == str(create_workspace_fixture._id)
    assert str(result[0].name) == create_workspace_fixture.name


def test_create_workspace():
    request_body = {
        "name": "new test workspace"
    }
    response = requests.post(url=base_url + "workspaces", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    created_resources.append({repo.Collection.WORKSPACE: Workspace.from_json(response.content.decode())._id})


def test_create_workspace_fail():
    request_body_with_wrong_parameter_name = {
        "workspace": "test workspace"
    }
    response = requests.post(url=base_url + "workspaces", json=request_body_with_wrong_parameter_name,
                             headers={"Authorization": token})
    assert response.status_code == 400


def test_invite_user(create_workspace_fixture):
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})


    assert response.status_code == 200

    invitation = src.services.invitation_service.get_invitation(workspace_id=create_workspace_fixture._id,
                                                                invitee_email_address=invitee_email_address)
    assert invitation is not None

    if invitation is not None:
        created_resources.append({repo.Collection.INVITATION: invitation._id})


def test_invite_user_already_invited(create_workspace_fixture):
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 400
    assert json.loads(response.content.decode())["description"] == "User already invited"
    created_resources.append({repo.Collection.INVITATION: src.services.invitation_service.get_invitation(
        workspace_id=create_workspace_fixture._id, invitee_email_address=invitee_email_address)._id})


def test_invite_user_already_in_workspace(create_workspace_fixture):
    invitee_email_address = settings.SMTP_EMAIL_ADDRESS
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 400
    print(type(response.content.decode()))
    assert json.loads(response.content.decode())["description"] == "User already in workspace"
