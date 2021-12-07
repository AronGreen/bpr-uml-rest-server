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
import src.services.teams_service as teams_service

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


def create_workspace_fixture(user_firebase_id: str):
    to_create = Workspace(
        _id=None,
        name="test workspace",
        users=list())
    workspace = workspace_service.create_workspace(to_create, user_firebase_id)
    created_resources[workspace.id] = Collection.WORKSPACE
    return workspace


def create_workspaces_fixture(user_firebase_id: str):
    workspace_1 = create_workspace_fixture(user_firebase_id)
    workspace_2 = create_workspace_fixture(user_firebase_id)
    return [workspace_1, workspace_2]


def create_team_fixture(workspaceId: ObjectId) -> Team:
    team = teams_service.create_team(Team(_id=None, workspaceId=workspaceId, name="create_team_fixture team", users=[]))
    created_resources[team.id] = Collection.TEAM
    return team

def add_users_to_team(team_id: ObjectId, users: list):
    team_users = []
    for user in users:
        team_users.append(TeamUser(userId=user.id))
    teams_service.add_users(team_id, team_users)


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

def create_project_fixture(workspace_id: ObjectId, title: str, user_firebase_id: str) -> Project:
    project = project_service.create_project(
            title=title,
            workspaceId=workspace_id,
            creator_firebase_id=user_firebase_id)
    created_resources[project._id] = Collection.PROJECT
    return project

def create_projects_fixture(workspace_id: ObjectId, user_firebase_id: str) -> list:
    project1 = create_project_fixture(workspace_id=workspace_id, title="project1", user_firebase_id=user_firebase_id)
    project2 = create_project_fixture(workspace_id=workspace_id, title="project2", user_firebase_id=user_firebase_id)
    return [project1, project2]

def add_users_to_workspace_fixture(workspace_id: ObjectId, users: list):
    for user in users:
        workspace_service.add_workspace_user(workspace_id, user.id)


def create_workspace_with_users_fixture(user_firebase_id: str):
    workspace = create_workspace_fixture(user_firebase_id)
    users = create_dummy_users_fixture()
    add_users_to_workspace_fixture(workspace_id=workspace.id, users=users)
    return {
        "workspace": workspace,
        "users": users
    }

def create_workspace_with_empty_team_fixture(user_firebase_id: str):
    workspace = create_workspace_fixture(user_firebase_id)
    team = create_team_fixture(workspace.id)
    return {
        "workspace": workspace,
        "team": team
    }

def create_workspace_with_users_and_empty_team_fixture(user_firebase_id: str):
    workspace_with_users = create_workspace_with_users_fixture(user_firebase_id)
    team = create_team_fixture(workspace_with_users["workspace"].id)
    workspace_with_users["team"] = team
    return workspace_with_users

def create_workspace_with_users_and_team_fixture(user_firebase_id: str):
    workspace_with_users = create_workspace_with_users_fixture(user_firebase_id)
    team = create_team_fixture(workspace_with_users["workspace"].id)
    add_users_to_team(team_id=team.id, users=workspace_with_users["users"])
    workspace_with_users["team"] = team
    return workspace_with_users

def create_workspaces_with_users_and_teams_fixture(user_firebase_id: str):
    user = create_dummy_user_with_token_fixture()

    workspace = create_workspace_fixture(user_firebase_id)
    workspace2 = create_workspace_fixture(user_firebase_id)

    add_users_to_workspace_fixture(workspace_id=workspace.id, users=[user["user"]])
    add_users_to_workspace_fixture(workspace_id=workspace2.id, users=[user["user"]])

    team1 = create_team_fixture(workspace.id)
    team2 = create_team_fixture(workspace.id)
    team3 = create_team_fixture(workspace2.id)
    team4 = create_team_fixture(workspace2.id)

    add_users_to_team(team_id=team1.id, users=[user["user"]])
    add_users_to_team(team_id=team2.id, users=[user["user"]])
    add_users_to_team(team_id=team3.id, users=[user["user"]])
    add_users_to_team(team_id=team4.id, users=[user["user"]])

    return_object = {
        "workspaces": [workspace, workspace2],
        "user": user["user"],
        "token": user["token"],
        "teams": [team1, team2, team3, team4]
    }

    return return_object

def create_workspace_with_project_fixture(user_firebase_id: str):
    workspace_with_users = create_workspace_with_users_fixture(user_firebase_id)
    workspace_project = create_project_fixture(workspace_id=workspace_with_users["workspace"].id, title="some project title", user_firebase_id=user_firebase_id)
    workspace_with_users["project"] = workspace_project
    return workspace_with_users

def create_workspace_with_users_and_projects_fixture(user_firebase_id: str):
    workspace_with_users = create_workspace_with_users_fixture(user_firebase_id)
    workspace_projects = create_projects_fixture(workspace_id=workspace_with_users["workspace"].id, user_firebase_id=user_firebase_id)
    workspace_with_users["projects"] = workspace_projects
    return workspace_with_users

def create_workspace_with_projects_and_teams_fixture(user_firebase_id: str):
    to_return = create_workspace_with_users_and_projects_fixture(user_firebase_id=user_firebase_id)
    team1 = create_team_fixture(workspaceId=to_return["workspace"].id)
    team2 = create_team_fixture(workspaceId=to_return["workspace"].id)
    to_return["teams"] = [team1, team2]
    return to_return

def make_user_invitations_fixture(user: User):
    dummy_user = create_dummy_user_with_token_fixture()
    workspaces = create_workspaces_fixture(user.firebaseId)

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

def remove_user_workspace_permission(workspace_id: ObjectId, permission: WorkspacePermission, user_id: ObjectId):
    permissions = [p.value for p in WorkspacePermission]
    permissions.remove(permission)
    workspace_service.update_user_permissions(workspace_id=workspace_id, user_id=user_id, permissions=permissions)
    

def remove_project_manager_check_from_user(project_id: ObjectId, user_id: ObjectId):
    project = project_service.get(project_id=project_id)
    for user in project.users:
        if user.userId == user_id:
            user.isProjectManager = False
    project_service.update_project(project)