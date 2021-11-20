import requests

from bpr_data.repository import Repository, Collection
from bpr_data.models.user import User
from bpr_data.models.workspace import Workspace
from bpr_data.models.invitation import Invitation
from bpr_data.models.project import Project
from bpr_data.models.team import Team

import src.services.workspace_service as workspace_service
import src.services.invitation_service as invitation_service
import settings

repo = Repository.get_instance(**settings.MONGO_CONN)

port_no = str(settings.APP_PORT)
port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/"

created_resources = []


def cleanup_fixture(resources: list):
    resources.extend(created_resources)
    for resource in resources:
        collection = list(resource.keys())[0]
        repo.delete(collection, _id=resource.get(collection))


def get_default_token_fixture():
    return get_token_fixture(settings.SMTP_EMAIL_ADDRESS, settings.SMTP_PASSWORD)


def get_token_fixture(email, password):
    details = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    # send post request
    r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(
        "AIzaSyDAuriepQen_J7sYEo4zKZLpFnjbhljsdQ"), data=details)
    if 'idToken' in r.json().keys():
        return r.json()['idToken']
    else:
        r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(
            "AIzaSyDAuriepQen_J7sYEo4zKZLpFnjbhljsdQ"), data=details)
        if 'idToken' in r.json().keys():
            return r.json()['idToken']


def create_user_fixture(token: str) -> User:
    response = requests.post(url=base_url + "users", headers={"Authorization": token})
    result = User.from_json(response.content.decode())
    created_resources.append({Collection.USER: result._id})
    return result


def create_workspace_fixture(token: str):
    request_body = {
        "name": "test workspace"
    }
    response = requests.post(url=base_url + "workspaces", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    created_resources.append({Collection.WORKSPACE: workspace.id})
    return workspace


def create_workspaces_fixture(token: str):
    workspace_1 = create_workspace_fixture(token)
    workspace_2 = create_workspace_fixture(token)
    return [workspace_1, workspace_2]


def create_team_fixture(token: str, workspaceId: str):
    team_name = "create_team_fixture team"
    request_body = {
        "name": team_name,
        "workspaceId": workspaceId
    }
    response = requests.post(url=base_url + "teams", json=request_body, headers={"Authorization": token})
    team = Team.from_json(response.content.decode())
    created_resources.append({Collection.TEAM: team._id})
    return team


def create_dummy_users_fixture():
    new_token_1 = get_token_fixture(settings.TEST_EMAIL_1, settings.TEST_PASSWORD_1)
    user_1 = create_user_fixture(new_token_1)
    new_token_2 = get_token_fixture(settings.TEST_EMAIL_2, settings.TEST_PASSWORD_2)
    user_2 = create_user_fixture(new_token_2)
    return [user_1, user_2]


def create_dummy_user_with_token_fixture():
    new_token_1 = get_token_fixture(settings.TEST_EMAIL_1, settings.TEST_PASSWORD_1)
    user_1 = create_user_fixture(new_token_1)
    user = {
        "user": user_1,
        "token": new_token_1
    }
    return user


def create_projects_fixture(workspace_id: str, token: str) -> list:
    request_body = {
        "title": "project 1",
        "workspaceId": str(workspace_id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    project1 = Project.from_json(response.content.decode())
    request_body = {
        "title": "project 2",
        "workspaceId": str(workspace_id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    project2 = Project.from_json(response.content.decode())

    created_resources.append({Collection.PROJECT: project1._id})
    created_resources.append({Collection.PROJECT: project2._id})

    return [project1, project2]


def add_users_to_workspace_fixture(workspace_id: str, users: list):
    for user in users:
        workspace_service.add_workspace_user(workspace_id, user.id)


def create_workspace_with_users_fixture(token: str):
    workspace = create_workspace_fixture(token)
    users = create_dummy_users_fixture()
    add_users_to_workspace_fixture(workspace_id=workspace.id, users=users)
    return {
        "workspace": workspace,
        "users": users
    }


def create_workspace_with_users_and_team_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    team = create_team_fixture(token, str(workspace_with_users["workspace"].id))
    workspace_with_users["team"] = team
    return workspace_with_users


def create_workspace_with_users_and_projects_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    # workspace = create_workspace_fixture(token)
    # users = create_dummy_users_fixture()
    # add_users_to_workspace_fixture(workspace_id=workspace.id, users=users)
    workspace_projects = create_projects_fixture(workspace_id=str(workspace_with_users["workspace"].id), token=token)
    workspace_with_users["projects"] = workspace_projects
    return workspace_with_users


def make_user_invitations_fixture(token: str, user: User):
    dummy_user = create_dummy_user_with_token_fixture()
    workspaces = create_workspaces_fixture(token)

    inv_1 = Invitation(
        _id=None,
        workspaceId=workspaces[0].id,
        inviterId=user._id,
        inviteeEmailAddress=dummy_user["user"].email
    )
    inv_2 = Invitation(
        _id=None,
        workspaceId=workspaces[1].id,
        inviterId=user._id,
        inviteeEmailAddress=dummy_user["user"].email
    )

    inv_1 = invitation_service.add_invitation(inv_1)
    inv_2 = invitation_service.add_invitation(inv_2)

    created_resources.append({Collection.INVITATION: inv_1._id})
    created_resources.append({Collection.INVITATION: inv_2._id})

    return {
        "user": dummy_user,
        "workspaces": workspaces,
        "invitations": [inv_1, inv_2]
    }
