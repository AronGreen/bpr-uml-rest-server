from bson import ObjectId
import pytest
import requests
import json

from bpr_data.repository import Repository, Collection
from bpr_data.models.workspace import Workspace, WorkspaceUser
from bpr_data.models.invitation import Invitation
from bpr_data.models.permission import WorkspacePermission
from bpr_data.models.project import Project, ProjectUser

from src.models.web_workspace_user import WebWorkspaceUser
import src.services.invitation_service
import src.services.workspace_service as workspace_service
import endpoint_test_util as util
import settings

repo = Repository.get_instance(**settings.MONGO_TEST_CONN)

created_resources = {}
port_no = str(settings.APP_PORT)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/workspaces"


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
    return util.create_workspace_fixture(user.firebaseId)


@pytest.fixture
def create_workspaces_fixture() -> list:
    return util.create_workspaces_fixture(user.firebaseId)


@pytest.fixture
def create_dummy_users_fixture() -> list:
    return util.create_dummy_users_fixture()

@pytest.fixture
def create_workspace_with_users_fixture() -> dict:
    return util.create_workspace_with_users_fixture(user.firebaseId)

@pytest.fixture
def invite_user_fixture() -> dict:
    workspace = util.create_workspace_fixture(user.firebaseId)
    second_user = util.create_dummy_user_with_token_fixture()
    invitee_email_address = second_user["user"].email
    request_body = {
        "workspaceId": str(workspace.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "/invitation", json=request_body,
                             headers={"Authorization": token})
    response = json.loads(response.content.decode())
    created_resources[response["_id"]] = Collection.INVITATION
    return {
        "user_with_token": second_user,
        "workspace_id": str(workspace.id),
        "invitation_id": str(response["_id"])
    }

@pytest.fixture
def create_dummy_user_with_token_fixture() -> dict:
    return util.create_dummy_user_with_token_fixture()

@pytest.fixture
def create_projects_fixture() -> list:
    workspace = util.create_workspace_fixture(user.firebaseId)
    projects = util.create_projects_fixture(workspace_id=workspace.id, user_firebase_id=user.firebaseId)

    project3 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace.id),
        teams=list(),
        users=[],
        folders=[])
    project3 = Project.from_dict(repo.insert(Collection.PROJECT, project3))

    workspace2 = util.create_workspace_fixture(user.firebaseId)
    project4 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace2.id),
        teams=list(),
        users=[user.id],
        folders=[])
    project4 = Project.from_dict(repo.insert(Collection.PROJECT, project4))
    created_resources[project3._id] = Collection.PROJECT
    created_resources[project4._id] = Collection.PROJECT

    projects.extend([project3, project4])
    return projects


def remove_user_workspace_permission(workspace_id: ObjectId, permission: WorkspacePermission):
    util.remove_user_workspace_permission(workspace_id=workspace_id, permission=permission, user_id=user.id)
    

def test_get_workspace(create_workspace_fixture):
    response = requests.get(url=base_url + "/" + str(create_workspace_fixture._id),
                            headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json(response.content.decode())
    assert str(result._id) == str(create_workspace_fixture._id)
    assert str(result.name) == create_workspace_fixture.name

def test_get_workspace_user_not_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "/" + str(create_workspace_fixture._id),
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_get_workspaces_for_user(create_workspace_fixture):
    response = requests.get(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    result = Workspace.from_json_list(response.content.decode())
    assert len(result) == 1
    assert str(result[0]._id) == str(create_workspace_fixture._id)
    assert str(result[0].name) == create_workspace_fixture.name


def test_create_workspace():
    request_body = {
        "name": "new test workspace"
    }
    response = requests.post(url=base_url, json=request_body, headers={"Authorization": token})
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
    response = requests.put(url=base_url + "/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
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
    response = requests.put(url=base_url + "/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    assert response.status_code == 200
    for user in workspace.users:
        if user["userId"] == str(create_workspace_with_users_fixture["users"][0].id):
            assert "MANAGE_PERMISSIONS" in user["permissions"]
            assert len(user["permissions"]) == 1
    
def test_change_user_permissions_without_permission(create_workspace_with_users_fixture):
    remove_user_workspace_permission(create_workspace_with_users_fixture["workspace"].id, WorkspacePermission.MANAGE_PERMISSIONS)
    request_body = {
        "permissions": [
            "MANAGE_PERMISSIONS",
            "MANAGE_TEAMS",
            "MANAGE_WORKSPACE"
        ]
    }
    response = requests.put(url=base_url + "/" + str(create_workspace_with_users_fixture["workspace"]._id) + "/" + str(create_workspace_with_users_fixture["users"][0].id) + "/permissions", json=request_body, headers={"Authorization": token})
    assert response.status_code == 403

def test_create_workspace_incomplete_request_body():
    request_body_with_wrong_parameter_name = {
        "workspace": "test workspace"
    }
    response = requests.post(url=base_url, json=request_body_with_wrong_parameter_name,
                             headers={"Authorization": token})
    assert response.status_code == 400


def test_invite_user(create_workspace_fixture):
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "/invitation", json=request_body,
                             headers={"Authorization": token})

    assert response.status_code == 200
    invitation = Invitation.from_json(response.content.decode())
    assert invitation.workspaceId == str(create_workspace_fixture.id)
    assert invitation.inviteeEmailAddress == invitee_email_address
    created_resources[invitation._id] = Collection.INVITATION

def test_invite_user_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(create_workspace_fixture.id, WorkspacePermission.MANAGE_WORKSPACE)
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "/invitation", json=request_body,
                             headers={"Authorization": token})

    assert response.status_code == 403


def test_invite_user_already_invited(create_workspace_fixture):
    invitee_email_address = "abc@gmail.com"
    request_body = {
        "workspaceId": str(create_workspace_fixture.id),
        "inviteeEmailAddress": invitee_email_address
    }
    response = requests.post(url=base_url + "/invitation", json=request_body,
                             headers={"Authorization": token})
    response = requests.post(url=base_url + "/invitation", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 400
    assert json.loads(response.content.decode())["description"] == "User already invited"
    created_resources[src.services.invitation_service.get_invitation(
        workspace_id=create_workspace_fixture._id, invitee_email_address=invitee_email_address)._id] = Collection.INVITATION

def test_respond_to_invitation(invite_user_fixture):
    request_body = {
        "invitationId": invite_user_fixture["invitation_id"],
        "accepted": True
    }
    response = requests.post(url=base_url + '/invitation/response', json=request_body,
                            headers={"Authorization": invite_user_fixture["user_with_token"]["token"]})
    print(response)
    assert response.status_code == 200

def test_remove_user_from_workspace(create_workspace_with_users_fixture):
    workspace_before_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    request_body = {
        "workspaceId": str(create_workspace_with_users_fixture["workspace"].id),
        "userId": str(create_workspace_with_users_fixture["users"][0].id)
    }
    response = requests.delete(url=base_url + '/user', json=request_body,
                            headers={"Authorization": token})                
    assert response.status_code == 200
    workspace_after_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    assert len(workspace_before_changes.users) == len(workspace_after_changes.users)+1
    for user in workspace_after_changes.users:
        assert user.userId != create_workspace_with_users_fixture["users"][0].id

def test_remove_user_from_workspace_without_permission(create_workspace_with_users_fixture):
    workspace_before_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    remove_user_workspace_permission(create_workspace_with_users_fixture["workspace"].id, WorkspacePermission.MANAGE_WORKSPACE)
    request_body = {
        "workspaceId": str(create_workspace_with_users_fixture["workspace"].id),
        "userId": str(create_workspace_with_users_fixture["users"][0].id)
    }
    response = requests.delete(url=base_url + '/user', json=request_body,
                            headers={"Authorization": token})                      
    assert response.status_code == 403
    workspace_after_changes = workspace_service.get_workspace(workspace_id=create_workspace_with_users_fixture["workspace"].id)
    assert len(workspace_before_changes.users) == len(workspace_after_changes.users)

def test_get_workspace_users(create_workspace_with_users_fixture):
    response = requests.get(url=base_url + '/' + str(create_workspace_with_users_fixture["workspace"].id) + "/users",
                            headers={"Authorization": token})
    assert response.status_code == 200
    print(response.content.decode())
    users = WebWorkspaceUser.from_json_list(response.content.decode())      
    assert len(users) == 3
    assert create_workspace_with_users_fixture["users"][0].id in [user._id for user in users]
    assert create_workspace_with_users_fixture["users"][1].id in [user._id for user in users]
    assert user.id in [user._id for user in users]

def test_get_workspace_users_when_not_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + '/' + str(create_workspace_fixture.id) + "/users",
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_update_workspace_name(create_workspace_fixture):
    new_name = "new name for workspace"
    request_body = {
        "name": new_name
    }
    response = requests.put(url=base_url + '/' + str(create_workspace_fixture.id), json=request_body,
                            headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    assert response.status_code == 200
    assert workspace.name == new_name

def test_update_workspace_name_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(create_workspace_fixture.id, WorkspacePermission.MANAGE_WORKSPACE)
    new_name = "new name for workspace"
    request_body = {
        "name": new_name
    }
    response = requests.put(url=base_url + '/' + str(create_workspace_fixture.id), json=request_body,
                            headers={"Authorization": token})
    assert response.status_code == 403

def test_delete_workspace(create_workspace_fixture):
    response = requests.delete(url=base_url + '/' + str(create_workspace_fixture.id),
                            headers={"Authorization": token})
    assert response.status_code == 200
    assert repo.find_one(collection=Collection.WORKSPACE, _id=create_workspace_fixture.id) == None

def test_delete_workspace_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(create_workspace_fixture.id, WorkspacePermission.MANAGE_WORKSPACE)
    response = requests.delete(url=base_url + '/' + str(create_workspace_fixture.id),
                            headers={"Authorization": token})
    assert response.status_code == 403
    assert workspace_service.get_workspace(workspace_id=create_workspace_fixture.id) != None

def test_get_workspace_user(create_workspace_fixture):
    response = requests.get(url=base_url + '/' + str(create_workspace_fixture.id) + "/user",
                            headers={"Authorization": token})
    assert response.status_code == 200
    current_user = WorkspaceUser.from_json(response.content.decode())
    assert str(user.id) == current_user.userId

def test_get_projects_for_workspace(create_projects_fixture):
    response = requests.get(url=base_url + "/" + str(create_projects_fixture[0].workspaceId) + "/projects",
                            headers={"Authorization": token})
    assert response.status_code == 200
    result = Project.from_json_list(response.content.decode())
    for project in result:
        project.users = ProjectUser.from_dict_list(project.users)
    assert len(result) == 2
    assert result[0].id == create_projects_fixture[0].id
    assert result[1].id == create_projects_fixture[1].id
    assert create_projects_fixture[2].id not in [project.id for project in result]
    assert create_projects_fixture[3].id not in [project.id for project in result]

def test_get_projects_for_workspace_user_not_in_project(create_projects_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "/" + str(create_projects_fixture[0].workspaceId) + "/projects",
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 200
    result = json.loads(response.content.decode())
    assert len(result) == 0