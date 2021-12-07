from bson.objectid import ObjectId
import requests

from bpr_data.repository import Repository, Collection
from bpr_data.models.user import User
from bpr_data.models.workspace import Workspace
from bpr_data.models.invitation import Invitation
from bpr_data.models.project import Project
from bpr_data.models.team import Team, TeamUser
from bpr_data.models.permission import WorkspacePermission

import src.services.workspace_service as workspace_service
import src.services.project_service as project_service
import src.services.invitation_service as invitation_service
import settings

repo = Repository.get_instance(**settings.MONGO_TEST_CONN)

port_no = str(settings.APP_PORT)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/"

created_resources = {}

def cleanup_fixture(resources: list):
    resources.update(created_resources)
    for resource_id in resources.keys():
        collection = resources[resource_id]
        repo.delete(collection, id=resource_id)


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
    created_resources[result._id]=Collection.USER
    return result


def create_workspace_fixture(token: str):
    request_body = {
        "name": "test workspace"
    }
    response = requests.post(url=base_url + "workspaces", json=request_body, headers={"Authorization": token})
    workspace = Workspace.from_json(response.content.decode())
    created_resources[workspace.id] = Collection.WORKSPACE
    return workspace


def create_workspaces_fixture(token: str):
    workspace_1 = create_workspace_fixture(token)
    workspace_2 = create_workspace_fixture(token)
    return [workspace_1, workspace_2]


def create_team_fixture(token: str, workspaceId: str) -> Team:
    team_name = "create_team_fixture team"
    request_body = {
        "name": team_name,
        "workspaceId": workspaceId
    }
    response = requests.post(url=base_url + "teams", json=request_body, headers={"Authorization": token})
    team = Team.from_json(response.content.decode())
    created_resources[team.id] = Collection.TEAM
    return team

def add_users_to_team(token: str, team_id: str, users: list):
    team_users = []
    for user in users:
        team_users.append(TeamUser(userId=user.id))

    request_body = {
        "users": TeamUser.as_json_list(team_users),
        "teamId": team_id
    }

    requests.post(url=base_url + "/teams/users", json=request_body, headers={"Authorization": token})


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

def create_project_fixture(workspace_id: str, title: str, token: str) -> Project:
    request_body = {
        "title": title,
        "workspaceId": str(workspace_id)
    }
    response = requests.post(url=base_url + "projects", json=request_body, headers={"Authorization": token})
    project = Project.from_json(response.content.decode())
    created_resources[project._id] = Collection.PROJECT
    return project

def create_projects_fixture(workspace_id: str, token: str) -> list:
    project1 = create_project_fixture(workspace_id=workspace_id, title="project1", token=token)
    project2 = create_project_fixture(workspace_id=workspace_id, title="project2", token=token)
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

def create_workspace_with_empty_team_fixture(token: str):
    workspace = create_workspace_fixture(token)
    team = create_team_fixture(token, str(workspace.id))
    return {
        "workspace": workspace,
        "team": team
    }

def create_workspace_with_users_and_empty_team_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    team = create_team_fixture(token, str(workspace_with_users["workspace"].id))
    workspace_with_users["team"] = team
    return workspace_with_users

def create_workspace_with_users_and_team_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    team = create_team_fixture(token, str(workspace_with_users["workspace"].id))
    add_users_to_team(token, team_id=str(team.id), users=workspace_with_users["users"])
    workspace_with_users["team"] = team
    return workspace_with_users

def create_workspaces_with_users_and_teams_fixture(token: str):
    user = create_dummy_user_with_token_fixture()

    workspace = create_workspace_fixture(token)
    workspace2 = create_workspace_fixture(token)

    add_users_to_workspace_fixture(workspace_id=str(workspace.id), users=[user["user"]])
    add_users_to_workspace_fixture(workspace_id=str(workspace2.id), users=[user["user"]])

    team1 = create_team_fixture(token, str(workspace.id))
    team2 = create_team_fixture(token, str(workspace.id))
    team3 = create_team_fixture(token, str(workspace2.id))
    team4 = create_team_fixture(token, str(workspace2.id))

    add_users_to_team(token, team_id=str(team1.id), users=[user["user"]])
    add_users_to_team(token, team_id=str(team2.id), users=[user["user"]])
    add_users_to_team(token, team_id=str(team3.id), users=[user["user"]])
    add_users_to_team(token, team_id=str(team4.id), users=[user["user"]])

    return_object = {
        "workspaces": [workspace, workspace2],
        "user": user["user"],
        "token": user["token"],
        "teams": [team1, team2, team3, team4]
    }

    return return_object

def create_workspace_with_project_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    workspace_project = create_project_fixture(workspace_id=str(workspace_with_users["workspace"].id), title="some project title", token=token)
    workspace_with_users["project"] = workspace_project
    return workspace_with_users

def create_workspace_with_users_and_projects_fixture(token: str):
    workspace_with_users = create_workspace_with_users_fixture(token)
    workspace_projects = create_projects_fixture(workspace_id=str(workspace_with_users["workspace"].id), token=token)
    workspace_with_users["projects"] = workspace_projects
    return workspace_with_users

def create_workspace_with_projects_and_teams_fixture(token: str):
    to_return = create_workspace_with_users_and_projects_fixture(token)
    team1 = create_team_fixture(token=token, workspaceId=str(to_return["workspace"].id))
    team2 = create_team_fixture(token=token, workspaceId=str(to_return["workspace"].id))
    to_return["teams"] = [team1, team2]
    return to_return

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

    created_resources[inv_1._id] = Collection.INVITATION
    created_resources[inv_2._id] = Collection.INVITATION

    return {
        "user": dummy_user,
        "workspaces": workspaces,
        "invitations": [inv_1, inv_2]
    }

def remove_user_workspace_permission(workspace_id: str, permission: WorkspacePermission, token: str, user_id: str):
    permissions = [p.value for p in WorkspacePermission]
    permissions.remove(permission)
    request_body = {
        "permissions": permissions
    }
    requests.put(url=base_url + "workspaces/" + workspace_id + "/" + user_id + "/permissions", json=request_body, headers={"Authorization": token})

def remove_project_manager_check_from_user(project_id: ObjectId, user_id: ObjectId):
    project = project_service.get(project_id=project_id)
    for user in project.users:
        if user.userId == user_id:
            user.isProjectManager = False
    project_service.update_project(project)