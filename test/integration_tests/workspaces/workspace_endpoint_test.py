import pytest
import requests
import settings
import src.repository as repo
from src.models.workspace import Workspace
from src.models.invitation import Invitation, InvitationGetModel
from src.models.user import User
import src.services.invitation_service
import endpoint_test_util as util
import json

created_resources = []
port_no = str(settings.APP_PORT)
port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/"


@pytest.fixture(autouse=True)
def before_test():
    global token
    global user
    token = util.get_default_token_fixture()
    user = util.create_user_fixture(token)
    yield
    util.cleanup_fixture(created_resources)


@pytest.fixture
def create_workspace_fixture() -> Workspace:
    return util.create_workspace_fixture(token)

@pytest.fixture
def create_workspaces_fixture() -> list:
    return util.create_workspaces_fixture(token)

@pytest.fixture
def create_dummy_users_fixture() -> list:
    return util.create_dummy_users_fixture()

@pytest.fixture
def make_user_invitations_fixture() -> list:
    return util.make_user_invitations_fixture(token, user)
    
def test_get_workspace(create_workspace_fixture):
    response = requests.get(url=base_url + "workspaces/" + str(create_workspace_fixture._id), headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json(response.content.decode())
    assert str(result._id) == str(create_workspace_fixture._id)
    assert str(result.name) == create_workspace_fixture.name

def test_get_workspaces_for_user(create_workspace_fixture):
    response = requests.get(url=base_url + "workspaces", headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json_list(response.content.decode())
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
    invitation = Invitation.from_json(response.content.decode())
    assert invitation.workspaceId == str(create_workspace_fixture.id)
    assert invitation.inviteeEmailAddress == invitee_email_address
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


def test_get_user_workspace_invitations(make_user_invitations_fixture):
    response = requests.get(url=base_url + 'users/invitations', headers={"Authorization": make_user_invitations_fixture["user"]["token"]})
    assert response.status_code == 200
    invitations = InvitationGetModel.from_json_list(response.content.decode())
    print(response.content.decode())
    print(invitations)
    for i in range(2):
        assert invitations[i].workspaceId == str(make_user_invitations_fixture["invitations"][i].workspaceId)
        assert invitations[i].inviteeEmailAddress == make_user_invitations_fixture["invitations"][i].inviteeEmailAddress
        assert invitations[i]._id == make_user_invitations_fixture["invitations"][i]._id
        assert invitations[i].inviterId == str(make_user_invitations_fixture["invitations"][i].inviterId)
        assert invitations[i].inviterUserName == user.name
        workspace_name=""
        for workspace in make_user_invitations_fixture["workspaces"]:
            if invitations[i].workspaceId == str(workspace._id):
                workspace_name = workspace.name
        assert invitations[i].workspaceName == workspace_name

    
