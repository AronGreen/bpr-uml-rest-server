import pytest
import requests
from bson import ObjectId
import json

from bpr_data.models.workspace import Workspace
from bpr_data.models.project import Project, ProjectTeam, ProjectUser
from bpr_data.repository import Repository, Collection
from bpr_data.models.permission import WorkspacePermission

import src.services.project_service as project_service
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
def create_projects_fixture() -> list:
    workspace = util.create_workspace_fixture(token)
    projects = util.create_projects_fixture(workspace_id=workspace.id, token=token)

    project3 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace.id),
        teams=list(),
        users=[])
    project3 = Project.from_dict(repo.insert(Collection.PROJECT, project3))

    workspace2 = util.create_workspace_fixture(token)
    project4 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace2.id),
        teams=list(),
        users=[user.id])
    project4 = Project.from_dict(repo.insert(Collection.PROJECT, project4))
    created_resources[project3._id] = Collection.PROJECT
    created_resources[project4._id] = Collection.PROJECT

    projects.extend([project3, project4])
    return projects


@pytest.fixture
def create_workspace_with_users_and_projects_fixture():
    return util.create_workspace_with_users_and_projects_fixture(token)

@pytest.fixture 
def create_workspace_with_projects_and_teams_fixture():
    return util.create_workspace_with_projects_and_teams_fixture(token)

@pytest.fixture
def create_dummy_user_with_token_fixture() -> dict:
    return util.create_dummy_user_with_token_fixture()

def remove_project_manager_check_from_user(project_id: ObjectId) -> dict:
    return util.remove_project_manager_check_from_user(project_id=project_id, user_id=user.id)

def remove_user_workspace_permission(workspace_id: str, permission: WorkspacePermission):
    util.remove_user_workspace_permission(workspace_id=workspace_id, permission=permission, user_id=str(user.id), token=token)

def test_create_project(create_workspace_fixture):
    project_title = "test project"
    request_body = {
        "title": project_title,
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    project = Project.from_json(response.content.decode())
    project.users = ProjectUser.from_dict_list(project.users)
    assert str(user.id) in [user.userId for user in project.users]
    assert project.title == project_title
    assert project.workspaceId == str(create_workspace_fixture.id)
    created_resources[project._id] = Collection.PROJECT

def test_create_project_without_permission(create_workspace_fixture):
    remove_user_workspace_permission(str(create_workspace_fixture.id), WorkspacePermission.MANAGE_WORKSPACE)
    project_title = "test project1"
    request_body = {
        "title": project_title,
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    assert response.status_code == 403
    assert repo.find_one(collection=Collection.PROJECT, name=project_title) == None

def test_create_project_without_being_in_workspace(create_workspace_fixture, create_dummy_user_with_token_fixture):
    project_title = "test project1"
    request_body = {
        "title": project_title,
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 403
    assert repo.find_one(collection=Collection.PROJECT, name=project_title) == None

def test_get_projects_for_workspace(create_projects_fixture):
    response = requests.get(url=base_url + "projects/workspace/" + create_projects_fixture[0].workspaceId,
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
    response = requests.get(url=base_url + "projects/workspace/" + create_projects_fixture[0].workspaceId,
                            headers={"Authorization": create_dummy_user_with_token_fixture["token"]})
    assert response.status_code == 200
    result = json.loads(response.content.decode())
    assert len(result) == 0

def test_add_users_to_project(create_workspace_with_users_and_projects_fixture):
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True, isProjectManager=False)
    user_2 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][1].id), isEditor=False, isProjectManager=False)

    request_body = {
        "users": ProjectUser.as_dict_list([user_1, user_2])
    }

    response = requests.post(url=base_url + "/projects/" + str(
        create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 200

    result = Project.from_json(response.content.decode())
    result.users = ProjectUser.from_dict_list(result.users)
    print(result)
    assert len(result.users) == 3
    assert str(user_1.userId) in [user.userId for user in result.users]
    assert str(user_2.userId) in [user.userId for user in result.users]

    for user in result.users:
        if str(user_1.userId) == user.userId:
            assert user.isEditor == user_1.isEditor
        if str(user_2.userId) == user.userId:
            assert user.isEditor == user_2.isEditor


def test_add_duplicate_users_to_project(create_workspace_with_users_and_projects_fixture):
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True, isProjectManager=False)

    request_body = {
        "users": ProjectUser.as_dict_list([user_1, user_1])
    }

    response = requests.post(url=base_url + "/projects/" + str(
        create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 400

    project = project_service.get(create_workspace_with_users_and_projects_fixture["projects"][0].id)

    assert len(project.users) == 1
    assert user_1.userId not in [user.userId for user in project.users]


def test_add_existing_user_to_project(create_projects_fixture):
    user_1 = ProjectUser(userId=str(user.id), isEditor=False, isProjectManager=False)
    request_body = {
        "users": ProjectUser.as_dict_list([user_1])
    }

    response = requests.post(url=base_url + "/projects/" + str(create_projects_fixture[0].id) + "/users",
                             json=request_body, headers={"Authorization": token})
    assert response.status_code == 400

    project = project_service.get(create_projects_fixture[0].id)

    assert len(project.users) == 1
    assert project.users[0].isEditor == True
    assert project.users[0].userId == ObjectId(user._id)

def test_replace_users_in_project(create_workspace_with_users_and_projects_fixture):
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True, isProjectManager=False)
    request_body = {
        "users": ProjectUser.as_dict_list([user_1])
    }
    response = requests.put(url=base_url + "/projects/" + str(
        create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 200
    result = Project.from_json(response.content.decode())
    result.users = ProjectUser.from_dict_list(result.users)
    assert len(result.users) == 1
    assert result.users[0].userId == str(create_workspace_with_users_and_projects_fixture["users"][0].id)

def test_replace_users_in_project_without_permissions(create_workspace_with_users_and_projects_fixture):
    remove_project_manager_check_from_user(create_workspace_with_users_and_projects_fixture["projects"][0].id)
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True, isProjectManager=False)
    request_body = {
        "users": ProjectUser.as_dict_list([user_1])
    }
    response = requests.put(url=base_url + "/projects/" + str(
        create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 403
    project = project_service.get(create_workspace_with_users_and_projects_fixture["projects"][0].id)
    assert len(project.teams) == 0

def test_replace_teams_in_project(create_workspace_with_projects_and_teams_fixture):
    team_1 = ProjectTeam(teamId=str(create_workspace_with_projects_and_teams_fixture["teams"][0].id), isEditor=True)
    team_2 = ProjectTeam(teamId=str(create_workspace_with_projects_and_teams_fixture["teams"][1].id), isEditor=False)
    request_body = {
        "teams": ProjectTeam.as_dict_list([team_1, team_2])
    }
    response = requests.put(url=base_url + "/projects/" + str(
        create_workspace_with_projects_and_teams_fixture["projects"][0].id) + "/teams", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 200
    result = Project.from_json(response.content.decode())
    result.teams = ProjectTeam.from_dict_list(result.teams)
    assert len(result.teams) == 2
    assert str(create_workspace_with_projects_and_teams_fixture["teams"][0].id) in [team.teamId for team in result.teams] 
    assert str(create_workspace_with_projects_and_teams_fixture["teams"][1].id) in [team.teamId for team in result.teams]

def test_replace_teams_in_project_without_permissions(create_workspace_with_projects_and_teams_fixture):
    remove_project_manager_check_from_user(create_workspace_with_projects_and_teams_fixture["projects"][0].id)
    team_1 = ProjectTeam(teamId=str(create_workspace_with_projects_and_teams_fixture["teams"][0].id), isEditor=True)
    team_2 = ProjectTeam(teamId=str(create_workspace_with_projects_and_teams_fixture["teams"][1].id), isEditor=False)
    request_body = {
        "teams": ProjectTeam.as_dict_list([team_1, team_2])
    }
    response = requests.put(url=base_url + "/projects/" + str(
        create_workspace_with_projects_and_teams_fixture["projects"][0].id) + "/teams", json=request_body,
                             headers={"Authorization": token})
    assert response.status_code == 403
    project = project_service.get(create_workspace_with_projects_and_teams_fixture["projects"][0].id)
    assert len(project.teams) == 0

def test_update_project_name(create_projects_fixture):
    new_title = "new project title"
    request_body = {
       "title": new_title 
    }
    response = requests.put(url=base_url + "/projects/" + str(create_projects_fixture[0].id), json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    project = Project.from_json(response.content.decode())
    assert project.title == new_title

def test_update_project_name_without_permissions(create_projects_fixture):
    remove_project_manager_check_from_user(create_projects_fixture[0].id)
    new_title = "bad title given by bad user"
    request_body = {
       "title": new_title 
    }
    response = requests.put(url=base_url + "/projects/" + str(create_projects_fixture[0].id), json=request_body, headers={"Authorization": token})
    assert response.status_code == 403
    project = project_service.get(create_projects_fixture[0].id)
    assert project.title != new_title

def test_delete_project(create_projects_fixture):
    response = requests.delete(url=base_url + "/projects/" + str(create_projects_fixture[0].id), headers={"Authorization": token})
    assert response.status_code == 200
    assert repo.find_one(collection=Collection.PROJECT, _id=create_projects_fixture[0].id) == None

def test_delete_project_without_permissions(create_projects_fixture):
    remove_project_manager_check_from_user(create_projects_fixture[0].id)
    response = requests.delete(url=base_url + "/projects/" + str(create_projects_fixture[0].id), headers={"Authorization": token})
    assert response.status_code == 403
    assert repo.find_one(collection=Collection.PROJECT, _id=create_projects_fixture[0].id) != None