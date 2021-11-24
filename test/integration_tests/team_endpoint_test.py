import pytest
import requests
import endpoint_test_util as util
from bpr_data.models.team import Team, TeamUser
from bpr_data.repository import Repository, Collection
import settings

repo = Repository.get_instance(**settings.MONGO_CONN)

created_resources = []
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
    return util.create_workspace_fixture(token)


@pytest.fixture
def create_workspace_with_users_and_team_fixture():
    return util.create_workspace_with_users_and_team_fixture(token)


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
    created_resources.append({Collection.TEAM: team._id})


def test_add_users_to_team(create_workspace_with_users_and_team_fixture):
    user_1 = TeamUser(userId=create_workspace_with_users_and_team_fixture["users"][0].id)
    user_2 = TeamUser(userId=create_workspace_with_users_and_team_fixture["users"][1].id)

    request_body = {
        "users": TeamUser.as_json_list([user_1, user_2]),
        "teamId": str(create_workspace_with_users_and_team_fixture["team"].id)
    }

    response = requests.post(url=base_url + "/teams/users", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    result = Team.from_json(response.content.decode())
    result.users = TeamUser.from_dict_list(result.users)
    assert len(result.users) == 2
    assert str(user_1.userId) in [user.userId for user in result.users]
    assert str(user_2.userId) in [user.userId for user in result.users]
