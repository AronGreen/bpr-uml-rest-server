import requests
import pytest
import json
from bpr_data.models.user import User
from bpr_data.models.team import Team
from bpr_data.repository import Repository, Collection
from bpr_data.models.invitation import InvitationGetModel

import endpoint_test_util as util
import settings

repo = Repository.get_instance(**settings.MONGO_TEST_CONN)


created_resources = {}
port_no = str(settings.APP_PORT)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/users"


@pytest.fixture(autouse=True)
def before_test():
    global token
    global user
    token = util.get_default_token_fixture()
    user = util.create_user_fixture(token)
    yield
    util.cleanup_fixture(created_resources)
    created_resources.clear()

@pytest.fixture
def make_user_invitations_fixture() -> list:
    return util.make_user_invitations_fixture(user)

@pytest.fixture
def create_workspaces_with_users_and_teams_fixture() -> dict:
    return util.create_workspaces_with_users_and_teams_fixture(user.firebaseId)

def test_ensure_user_exists():
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    assert settings.SMTP_EMAIL_ADDRESS == user.email
    created_resources[user._id] = Collection.USER

def test_get_user_workspace_invitations(make_user_invitations_fixture):
    response = requests.get(url=base_url + '/invitations',
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

def test_get_teams_for_user(create_workspaces_with_users_and_teams_fixture):
    response = requests.get(base_url + "/teams", headers={"Authorization": create_workspaces_with_users_and_teams_fixture["token"]})
    assert response.status_code == 200
    teams = Team.from_json_list(response.content.decode())
    assert create_workspaces_with_users_and_teams_fixture["teams"][0].id in [team.id for team in teams]
    assert create_workspaces_with_users_and_teams_fixture["teams"][1].id in [team.id for team in teams]
    assert create_workspaces_with_users_and_teams_fixture["teams"][2].id in [team.id for team in teams]
    assert create_workspaces_with_users_and_teams_fixture["teams"][3].id in [team.id for team in teams]

def test_get_teams_for_user_empty_result():
    response = requests.get(base_url + "/teams", headers={"Authorization": token})
    assert response.status_code == 200
    teams = json.loads(response.content.decode())
    assert len(teams) == 0
