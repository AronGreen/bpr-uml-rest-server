import pytest
import requests
import settings
import endpoint_test_util as util
from src.models.workspace import Workspace
from src.models.project import Project, ProjectUser
import src.services.project_service as project_service
import src.repository as repo
from bson import ObjectId

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
def create_projects_fixture() -> list:
    workspace = util.create_workspace_fixture(token)
    projects = util.create_projects_fixture(workspace_id=workspace.id, token=token)

    project3 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace.id),
        teams=list(),
        users=[])
    project3 = Project.from_dict(repo.insert(repo.Collection.PROJECT, project3))
    
    workspace2 = util.create_workspace_fixture(token)
    project4 = Project(
        _id=None,
        title="some title",
        workspaceId=ObjectId(workspace2.id),
        teams=list(),
        users=[user.id])
    project4 = Project.from_dict(repo.insert(repo.Collection.PROJECT, project4))
    created_resources.append({repo.Collection.PROJECT: project3._id})
    created_resources.append({repo.Collection.PROJECT: project4._id})

    projects.extend([project3, project4])
    return projects

@pytest.fixture
def create_workspace_with_users_and_projects_fixture():
    return util.create_workspace_with_users_and_projects_fixture(token)

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
    created_resources.append({repo.Collection.PROJECT: project._id})

def test_get_projects_for_workspace(create_projects_fixture):
    response = requests.get(url=base_url + "workspaces/" + create_projects_fixture[0].workspaceId + "/projects", headers={"Authorization": token})
    assert response.status_code == 200
    result = Project.from_json_list(response.content.decode())

    print(result)

    for project in result:
        project.users = ProjectUser.from_dict_list(project.users)

    print(result)

    assert len(result) == 2
    assert result[0].id == create_projects_fixture[0].id
    assert result[1].id == create_projects_fixture[1].id
    assert create_projects_fixture[2].id not in [project.id for project in result]
    assert create_projects_fixture[3].id not in [project.id for project in result]

def test_add_users_to_project(create_workspace_with_users_and_projects_fixture):
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True)
    user_2 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][1].id), isEditor=False)

    request_body = {
        "users": ProjectUser.as_dict_list([user_1, user_2])
    }
    
    response = requests.post(url=base_url + "/projects/" + str(create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body, headers={"Authorization": token})
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
    user_1 = ProjectUser(userId=str(create_workspace_with_users_and_projects_fixture["users"][0].id), isEditor=True)

    request_body = {
        "users": ProjectUser.as_dict_list([user_1, user_1])
    }
    
    response = requests.post(url=base_url + "/projects/" + str(create_workspace_with_users_and_projects_fixture["projects"][0].id) + "/users", json=request_body, headers={"Authorization": token})
    assert response.status_code == 400

    project = project_service.get(str(create_workspace_with_users_and_projects_fixture["projects"][0].id))
    
    assert len(project.users) == 1
    assert user_1.userId not in [user.userId for user in project.users]

def test_add_existing_user_to_project(create_projects_fixture):
    user_1 = ProjectUser(userId=str(user.id), isEditor=False)
    request_body = {
        "users": ProjectUser.as_dict_list([user_1])
    }
    
    response = requests.post(url=base_url + "/projects/" + str(create_projects_fixture[0].id) + "/users", json=request_body, headers={"Authorization": token})
    assert response.status_code == 400

    project = project_service.get(str(create_projects_fixture[0].id))
    
    assert len(project.users) == 1
    assert project.users[0].isEditor == True
    assert project.users[0].userId == ObjectId(user._id)