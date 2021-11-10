import pytest
import requests
import settings
import endpoint_test_util as util
from src.models.workspace import Workspace
from src.models.project import Project
import src.repository as repo
from bson import ObjectId

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
    return util.create_workspace_fixture(token)

@pytest.fixture
def create_projects_fixture() -> list:
    workspace = util.create_workspace_fixture(token)
    request_body = {
        "title": "project 1",
        "workspaceId": str(workspace.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    project1 = Project.from_json(response.content.decode())
    request_body = {
        "title": "project 2",
        "workspaceId": str(workspace.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    project2 = Project.from_json(response.content.decode())

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
    created_resources.append({repo.Collection.PROJECT: project1._id})
    created_resources.append({repo.Collection.PROJECT: project2._id})
    created_resources.append({repo.Collection.PROJECT: project3._id})
    created_resources.append({repo.Collection.PROJECT: project4._id})

    return [project1, project2, project3, project4]

def test_create_project(create_workspace_fixture):
    project_title = "test project"
    request_body = {
        "title": project_title,
        "workspaceId": str(create_workspace_fixture.id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    assert response.status_code == 200
    project = Project.from_json(response.content.decode())
    assert str(user.id) in project.users
    assert project.title == project_title
    assert project.workspaceId == str(create_workspace_fixture.id)
    created_resources.append({repo.Collection.PROJECT: project._id})

def test_get_projects_for_workspace(create_projects_fixture):
    response = requests.get(url=base_url + "workspaces/" + create_projects_fixture[0].workspaceId + "/projects", headers={"Authorization": token})
    assert response.status_code == 200
    result = Project.from_json_list(response.content.decode())
    assert len(result) == 2
    assert result[0].id == create_projects_fixture[0].id
    assert result[1].id == create_projects_fixture[1].id
    assert create_projects_fixture[2].id not in [project.id for project in result]
    assert create_projects_fixture[3].id not in [project.id for project in result]

