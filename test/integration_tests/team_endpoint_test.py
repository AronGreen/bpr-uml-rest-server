from bson.objectid import ObjectId
import pytest
import requests
import endpoint_test_util as util
from bpr_data.models.team import Team, TeamUser
from bpr_data.repository import Repository, Collection
import settings
from bpr_data.models.permission import WorkspacePermission
import src.services.teams_service as teams_service

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
def create_workspace_fixture():
    return util.create_workspace_fixture(user.firebaseId)


@pytest.fixture
def create_workspace_with_users_and_empty_team_fixture():
    return util.create_workspace_with_users_and_empty_team_fixture(user.firebaseId)

@pytest.fixture
def create_workspace_with_users_and_team_fixture():
    return util.create_workspace_with_users_and_team_fixture(user.firebaseId)

@pytest.fixture
def create_workspace_with_empty_team_fixture():
    return util.create_workspace_with_empty_team_fixture(user.firebaseId)

@pytest.fixture
def create_dummy_user_with_token_fixture() -> dict:
    return util.create_dummy_user_with_token_fixture()

def remove_user_workspace_permission(workspace_id: ObjectId, permission: WorkspacePermission):
    util.remove_user_workspace_permission(workspace_id=workspace_id, permission=permission, user_id=user.id)

def test_get_workspace_teams(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "workspaces/" + str(create_workspace_with_empty_team_fixture["workspace"].id) + "/teams", headers={"Authorization": token})
    assert response.status_code == 200
    teams = Team.from_json_list(response.content.decode())
    assert len(teams) == 1
    assert teams[0].id == create_workspace_with_empty_team_fixture["team"].id

def test_get_workspace_teams_without_being_in_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "workspaces/" + str(create_workspace_with_empty_team_fixture["workspace"].id) + "/teams", headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_create_team(create_workspace_fixture):
    team_name = "test_create_team team"
    request_body = {
        "name": team_name,
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "teams", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    team = Team.from_json(response.content.decode())
    team.users = TeamUser.from_dict_list(team.users)
    assert len(team.users) == 0
    assert team.name == team_name
    assert team.workspaceId == str(create_workspace_fixture.id)
    created_resources[team._id] = Collection.TEAM

def test_create_team_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(create_workspace_fixture.id, WorkspacePermission.MANAGE_TEAMS)
    request_body = {
        "name": "team_name1",
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "teams", json=request_body, headers={"Authorization": token})
    assert response.status_code == 403
    assert repo.find_one(collection=Collection.TEAM, name="team_name1") == None

def test_create_team_without_being_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    remove_user_workspace_permission(create_workspace_fixture.id, WorkspacePermission.MANAGE_TEAMS)
    request_body = {
        "name": "team_name2",
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "teams", json=request_body, headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403
    assert repo.find_one(collection=Collection.TEAM, name="team_name2") == None

def test_add_users_to_team(create_workspace_with_users_and_empty_team_fixture):
    user_1 = TeamUser(userId=create_workspace_with_users_and_empty_team_fixture["users"][0].id)
    user_2 = TeamUser(userId=create_workspace_with_users_and_empty_team_fixture["users"][1].id)

    request_body = {
        "users": TeamUser.as_json_list([user_1, user_2]),
        "teamId": str(create_workspace_with_users_and_empty_team_fixture["team"].id)
    }

    response = requests.post(url=base_url + "/teams/users", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    result = Team.from_json(response.content.decode())
    result.users = TeamUser.from_dict_list(result.users)
    assert len(result.users) == 2
    assert str(user_1.userId) in [user.userId for user in result.users]
    assert str(user_2.userId) in [user.userId for user in result.users]

def test_add_users_to_team_without_permission(create_workspace_with_users_and_empty_team_fixture):
    remove_user_workspace_permission(workspace_id=create_workspace_with_users_and_empty_team_fixture["workspace"].id, permission=WorkspacePermission.MANAGE_TEAMS)
    user_1 = TeamUser(userId=create_workspace_with_users_and_empty_team_fixture["users"][0].id)
    user_2 = TeamUser(userId=create_workspace_with_users_and_empty_team_fixture["users"][1].id)

    request_body = {
        "users": TeamUser.as_json_list([user_1, user_2]),
        "teamId": str(create_workspace_with_users_and_empty_team_fixture["team"].id)
    }

    response = requests.post(url=base_url + "/teams/users", json=request_body, headers={"Authorization": token})
    assert response.status_code == 403
    team = teams_service.get_team(create_workspace_with_users_and_empty_team_fixture["team"].id)
    assert len(team.users) == 0

def test_add_users_to_team_without_being_in_the_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    user_1 = TeamUser(userId=create_dummy_user_with_token_fixture["user"].id)

    request_body = {
        "users": TeamUser.as_json_list([user_1]),
        "teamId": str(create_workspace_with_empty_team_fixture["team"].id)
    }

    response = requests.post(url=base_url + "/teams/users", json=request_body, headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403
    team = teams_service.get_team(create_workspace_with_empty_team_fixture["team"].id)
    assert len(team.users) == 0

def test_replace_users_in_team(create_workspace_with_users_and_team_fixture):
    user_1 = TeamUser(userId=str(create_workspace_with_users_and_team_fixture["users"][0].id))

    request_body = {
        "users": TeamUser.as_dict_list([user_1])
    }

    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_users_and_team_fixture["team"].id) + "/users", 
                            json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    result = Team.from_json(response.content.decode())
    result.users = TeamUser.from_dict_list(result.users)
    assert len(result.users) == 1
    assert str(user_1.userId) in [user.userId for user in result.users]

def test_replace_users_in_team_without_permission(create_workspace_with_users_and_empty_team_fixture):
    remove_user_workspace_permission(workspace_id=create_workspace_with_users_and_empty_team_fixture["workspace"].id, permission=WorkspacePermission.MANAGE_TEAMS)
    user_1 = TeamUser(userId=str(create_workspace_with_users_and_empty_team_fixture["users"][0].id))

    request_body = {
        "users": TeamUser.as_dict_list([user_1])
    }

    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_users_and_empty_team_fixture["team"].id) + "/users", 
                            json=request_body, headers={"Authorization": token})
    assert response.status_code == 403
    team = teams_service.get_team(create_workspace_with_users_and_empty_team_fixture["team"].id)
    assert len(team.users) == 0

def test_replace_users_in_team_without_being_in_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    user_1 = TeamUser(userId=str(create_dummy_user_with_token_fixture["user"].id))

    request_body = {
        "users": TeamUser.as_dict_list([user_1])
    }

    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id) + "/users", 
                            json=request_body, headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403
    team = teams_service.get_team(create_workspace_with_empty_team_fixture["team"].id)
    assert len(team.users) == 0

def test_update_team_name(create_workspace_with_empty_team_fixture):
    team_name = "team_name"
    request_body = {
        "name": team_name
    }
    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            json=request_body, headers={"Authorization": token})
    print(response.content.decode())
    team = Team.from_json(response.content.decode())
    assert response.status_code == 200
    assert team.name == team_name

def test_update_team_name_without_permission(create_workspace_with_empty_team_fixture):
    remove_user_workspace_permission(workspace_id=create_workspace_with_empty_team_fixture["workspace"].id, permission=WorkspacePermission.MANAGE_TEAMS)
    team_name = "team_name_1"
    request_body = {
        "name": team_name
    }
    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            json=request_body, headers={"Authorization": token})
    assert response.status_code == 403

def test_update_team_name_without_being_in_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    team_name = "team_name_1"
    request_body = {
        "name": team_name
    }
    response = requests.put(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            json=request_body, headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_get_team_by_team_id(create_workspace_with_users_and_team_fixture):
    response = requests.get(url=base_url + "/teams/" + str(create_workspace_with_users_and_team_fixture["team"].id), 
                            headers={"Authorization": token})
    assert response.status_code == 200
    team = Team.from_json(response.content.decode())
    assert str(create_workspace_with_users_and_team_fixture["users"][0].id) in [user["userId"] for user in team.users]
    assert str(create_workspace_with_users_and_team_fixture["users"][1].id) in [user["userId"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][0].name in [user["user"]["name"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][1].name in [user["user"]["name"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][0].email in [user["user"]["email"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][1].email in [user["user"]["email"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][0].firebaseId in [user["user"]["firebaseId"] for user in team.users]
    assert create_workspace_with_users_and_team_fixture["users"][1].firebaseId in [user["user"]["firebaseId"] for user in team.users]

def test_get_team_by_team_id_without_being_in_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    response = requests.get(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403

def test_delete_team(create_workspace_with_empty_team_fixture):
    response = requests.delete(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            headers={"Authorization": token})
    assert response.status_code == 200
    assert repo.find_one(collection=Collection.TEAM, _id=create_workspace_with_empty_team_fixture["team"].id) == None

def test_delete_team_without_permission(create_workspace_with_empty_team_fixture):
    remove_user_workspace_permission(workspace_id=create_workspace_with_empty_team_fixture["workspace"].id, permission=WorkspacePermission.MANAGE_TEAMS)
    response = requests.delete(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            headers={"Authorization": token})
    assert response.status_code == 403
    assert teams_service.get_team(create_workspace_with_empty_team_fixture["team"].id) is not None

def test_delete_team_without_being_in_workspace(create_workspace_with_empty_team_fixture, create_dummy_user_with_token_fixture):
    remove_user_workspace_permission(workspace_id=create_workspace_with_empty_team_fixture["workspace"].id, permission=WorkspacePermission.MANAGE_TEAMS)
    response = requests.delete(url=base_url + "/teams/" + str(create_workspace_with_empty_team_fixture["team"].id), 
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403
    assert teams_service.get_team(create_workspace_with_empty_team_fixture["team"].id) is not None