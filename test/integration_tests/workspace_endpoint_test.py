import pytest
import requests
import json

from bpr_data.repository import Repository, Collection
from bpr_data.models.workspace import Workspace, WorkspaceUser
from bpr_data.models.invitation import Invitation, InvitationGetModel
from bpr_data.models.permission import WorkspacePermission

from src.models.web_workspace_user import WebWorkspaceUser
import src.services.invitation_service
import src.services.workspace_service as workspace_service
import endpoint_test_util as util
import settings

repo = Repository.get_instance(**settings.MONGO_TEST_CONN)

created_resources = {}
port_no = str(settings.APP_PORT)
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

@pytest.fixture
def create_workspace_with_users_fixture() -> dict:
    return util.create_workspace_with_users_fixture(token)

@pytest.fixture
def invite_user_fixture() -> dict:
    workspace = util.create_workspace_fixture(token)
    user = util.create_dummy_user_with_token_fixture()
    invitee_email_address = user["user"].email
    request_body = {
        "workspaceId": str(workspace.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})
    response = json.loads(response.content.decode())
    created_resources[response["_id"]] = Collection.INVITATION
    return {
        "user_with_token": user,
        "workspace_id": str(workspace.id),
        "invitation_id": str(response["_id"])
    }

@pytest.fixture
def create_dummy_user_with_token_fixture() -> dict:
    return util.create_dummy_user_with_token_fixture()

def remove_user_workspace_permission(workspace_id: str, permission: WorkspacePermission):
    util.remove_user_workspace_permission(workspace_id=workspace_id, permission=permission, user_id=str(user.id), token=token)
    

def test_get_workspace(create_workspace_fixture):
    response = requests.get(url=base_url + "workspaces/" + str(create_workspace_fixture._id),
                            headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json(response.content.decode())
    assert str(result._id) == str(create_workspace_fixture._id)
    assert str(result.name) == create_workspace_fixture.name

def test_get_workspace_user_not_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "workspaces/" + str(create_workspace_fixture._id),
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

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
    created_resources[Workspace.from_json(response.content.decode())._id] = Collection.WORKSPACE

def test_change_user_permissions(create_workspace_with_users_fixture):
    request_body = {
        "permissions": [
            "MANAGE_PERMISSIONS",
            "MANAGE_TEAMS",
            "MANAGE_WORKSPACE"
        ]
    }
    response = requests.put(url=base_url + "workspaces/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    assert response.status_code == 200
    for user in workspace.users:
        if user["userId"] == str(create_workspace_with_users_fixture["users"][0].id):
            assert all(item in user["permissions"] for item in ["MANAGE_PERMISSIONS", "MANAGE_TEAMS", "MANAGE_WORKSPACE"])
            assert len(user["permissions"]) == 3

    request_body = {
        "permissions": [
            "MANAGE_PERMISSIONS"
        ]
    }
    response = requests.put(url=base_url + "workspaces/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    assert response.status_code == 200
    for user in workspace.users:
        if user["userId"] == str(create_workspace_with_users_fixture["users"][0].id):
            assert "MANAGE_PERMISSIONS" in user["permissions"]
            assert len(user["permissions"]) == 1
    
def test_change_user_permissions_without_permission(create_workspace_with_users_fixture):
    remove_user_workspace_permission(str(create_workspace_with_users_fixture["workspace"].id), WorkspacePermission.MANAGE_PERMISSIONS)
    request_body = {
        "permissions": [
            "MANAGE_PERMISSIONS",
            "MANAGE_TEAMS",
            "MANAGE_WORKSPACE"
        ]
    }
    response = requests.put(url=base_url + "workspaces/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
    assert response.status_code == 403

def test_create_workspace_incomplete_request_body():
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
    created_resources[invitation._id] = Collection.INVITATION

def test_invite_user_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(str(create_workspace_fixture.id), WorkspacePermission.MANAGE_WORKSPACE)
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "workspaces/invitation", json=request_body,
                             headers={"Authorization": token})

    assert response.status_code == 403


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
    created_resources[src.services.invitation_service.get_invitation(
        workspace_id=create_workspace_fixture._id, invitee_email_address=invitee_email_address)._id] = Collection.INVITATION


def test_get_user_workspace_invitations(make_user_invitations_fixture):
    response = requests.get(url=base_url + 'users/invitations',
                            headers={"Authorization": make_user_invitations_fixture["user"]["token"]})
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
        workspace_name = ""
        for workspace in make_user_invitations_fixture["workspaces"]:
            if invitations[i].workspaceId == str(workspace._id):
                workspace_name = workspace.name
        assert invitations[i].workspaceName == workspace_name

def test_respond_to_invitation(invite_user_fixture):
    request_body = {
        "invitationId": invite_user_fixture["invitation_id"],
        "accepted": True
    }
    response = requests.post(url=base_url + 'workspaces/invitation/response', json=request_body,
                            headers={"Authorization": invite_user_fixture["user_with_token"]["token"]})
    print(response)
    assert response.status_code == 200

def test_remove_user_from_workspace(create_workspace_with_users_fixture):
    workspace_before_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    request_body = {
        "workspaceId": str(create_workspace_with_users_fixture["workspace"].id),
        "userId": str(create_workspace_with_users_fixture["users"][0].id)
    }
    response = requests.delete(url=base_url + 'workspaces/user', json=request_body,
                            headers={"Authorization": token})                
    assert response.status_code == 200
    workspace_after_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    assert len(workspace_before_changes.users) == len(workspace_after_changes.users)+1
    for user in workspace_after_changes.users:
        assert user.userId != create_workspace_with_users_fixture["users"][0].id

def test_remove_user_from_workspace_without_permission(create_workspace_with_users_fixture):
    workspace_before_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    remove_user_workspace_permission(str(create_workspace_with_users_fixture["workspace"].id), WorkspacePermission.MANAGE_WORKSPACE)
    request_body = {
        "workspaceId": str(create_workspace_with_users_fixture["workspace"].id),
        "userId": str(create_workspace_with_users_fixture["users"][0].id)
    }
    response = requests.delete(url=base_url + 'workspaces/user', json=request_body,
                            headers={"Authorization": token})                      
    assert response.status_code == 403
    workspace_after_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    assert len(workspace_before_changes.users) == len(workspace_after_changes.users)

def test_get_workspace_users(create_workspace_with_users_fixture):
    response = requests.get(url=base_url + 'workspaces/' + str(create_workspace_with_users_fixture["workspace"].id) + "/users",
                            headers={"Authorization": token})
    assert response.status_code == 200
    print(response.content.decode())
    users = WebWorkspaceUser.from_json_list(response.content.decode())      
    assert len(users) == 3
    assert create_workspace_with_users_fixture["users"][0].id in [user._id for user in users]
    assert create_workspace_with_users_fixture["users"][1].id in [user._id for user in users]
    assert user.id in [user._id for user in users]

def test_get_workspace_users_when_not_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + 'workspaces/' + str(create_workspace_fixture.id) + "/users",
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_update_workspace_name(create_workspace_fixture):
    new_name = "new name for workspace"
    request_body = {
        "name": new_name
    }
    response = requests.put(url=base_url + 'workspaces/' + str(create_workspace_fixture.id), json=request_body,
                            headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    assert response.status_code == 200
    assert workspace.name == new_name

def test_update_workspace_name_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(str(create_workspace_fixture.id), WorkspacePermission.MANAGE_WORKSPACE)
    new_name = "new name for workspace"
    request_body = {
        "name": new_name
    }
    response = requests.put(url=base_url + 'workspaces/' + str(create_workspace_fixture.id), json=request_body,
                            headers={"Authorization": token})
    assert response.status_code == 403

def test_delete_workspace(create_workspace_fixture):
    response = requests.delete(url=base_url + 'workspaces/' + str(create_workspace_fixture.id),
                            headers={"Authorization": token})
    assert response.status_code == 200
    assert repo.find_one(collection=Collection.WORKSPACE, _id=create_workspace_fixture.id) == None

def test_delete_workspace_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(str(create_workspace_fixture.id), WorkspacePermission.MANAGE_WORKSPACE)
    response = requests.delete(url=base_url + 'workspaces/' + str(create_workspace_fixture.id),
                            headers={"Authorization": token})
    assert response.status_code == 403
    assert workspace_service.get_workspace(workspace_id=create_workspace_fixture.id) != None

def test_get_workspace_user(create_workspace_fixture):
    response = requests.get(url=base_url + 'workspaces/' + str(create_workspace_fixture.id) + "/user",
                            headers={"Authorization": token})
    assert response.status_code == 200
    current_user = WorkspaceUser.from_json(response.content.decode())
    assert str(user.id) == current_user.userId