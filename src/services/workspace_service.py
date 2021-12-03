from __future__ import annotations

from bson import ObjectId
from flask import g, abort

from bpr_data.repository import Repository, Collection
from bpr_data.models.invitation import Invitation
from bpr_data.models.user import User
from bpr_data.models.workspace import Workspace, WorkspaceUser
from bpr_data.models.permission import WorkspacePermission
from bpr_data.models.team import Team

import src.util.email_utils as email
import src.services.email_service as email_service
import src.services.users_service as users_service
import src.services.invitation_service as invitation_service
import src.services.permission_service as permission_service
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.WORKSPACE


def create_workspace(workspace: Workspace) -> Workspace:
    creator = User.from_dict(db.find_one(Collection.USER, firebaseId=g.firebase_id))
    workspace_user = WorkspaceUser(userId = creator.id, permissions=list(WorkspacePermission))
    workspace.users = [workspace_user]
    created_workspace = db.insert(collection, workspace)
    if created_workspace is not None:
        return Workspace.from_dict(created_workspace)


def get_workspace(workspace_id: ObjectId) -> Workspace:
    find_result = db.find_one(collection, _id=workspace_id)
    if find_result is not None:
        workspace = Workspace.from_dict(find_result)
        workspace.users = WorkspaceUser.from_dict_list(workspace.users)
        return workspace
    else:
        abort(404, description="Workspace not found")

def get_user_workspaces(firebase_id: str) -> list:
    # TODO: filter so only current users workspaces are present
    user = users_service.get_user_by_firebase_id(firebase_id)
    find_result = db.find(collection=collection, nested_conditions={'users.userId': user.id})
    if find_result is not None:
        return Workspace.from_dict_list(find_result)


# TODO: move to invitation service
def invite_user(invitation: Invitation) -> str:
    workspace = get_workspace(invitation.workspaceId)
    if workspace is None:
        return abort(400, description="Workspace does not exist")

    if invitation_service.get_invitation(invitation.workspaceId, invitation.inviteeEmailAddress):
        abort(400, description="User already invited")
    inviter = users_service.get_user_by_firebase_id(g.firebase_id)
    invitation.inviterId = inviter.id
    user = users_service.get_user_by_email_address(invitation.inviteeEmailAddress)
    if user is None:
        if email.is_valid(invitation.inviteeEmailAddress):
            subject = "Diagramz invitation"
            message = "{} sent you an invitation on Diagramz to collaborate on {}".format(g.user_name, workspace.name)
            email_service.send_email(invitation.inviteeEmailAddress, subject, message)
            return invitation_service.add_invitation(invitation)
        else:
            abort(400, description="Invalid email")
    else:
        if user.id not in workspace.users:
            return invitation_service.add_invitation(invitation)
        else:
            abort(400, description="User already in workspace")


# TODO: move to invitation service
def respond_to_invitation(invitation_id: str | ObjectId, accepted: bool) -> str:
    invitation = invitation_service.get_invitation_by_id(invitation_id)
    if g.user_email != invitation.inviteeEmailAddress:
        abort(401)
    if invitation is None:
        abort(404, description="Invitation not found")
    return_text = ""
    if accepted:
        user = users_service.get_user_by_email_address(invitation.inviteeEmailAddress)
        workspace = get_workspace(invitation.workspaceId)
        if user is not None and workspace is not None:
            add_workspace_user(invitation.workspaceId, user.id)
            return_text = "User added"
    else:
        return_text = "Invitation declined"
    invitation_service.delete_invitation(invitation_id)
    return return_text


def add_workspace_user(workspace_id: str | ObjectId, user_id: str | ObjectId) -> bool:
    if not are_users_in_workspace(ObjectId(workspace_id), [ObjectId(user_id)]):
        return db.push(
            collection=Collection.WORKSPACE,
            document_id=workspace_id,
            field_name='users',
            item=WorkspaceUser(userId=user_id, permissions=[])
        )


def remove_workspace_user(workspace_id: str | ObjectId, user_id: str | ObjectId) -> bool:
    return db.pull(
        collection=Collection.WORKSPACE,
        document_id=workspace_id,
        field_name='users',
        item=user_id
    )


def get_workspace_users(workspaceId: str | ObjectId) -> list:
    workspace = Workspace.from_dict(db.find_one(collection, id=workspaceId))
    workspace.users = WorkspaceUser.from_dict_list(workspace.users)
    if workspace.users is None:
        return list()
    return [users_service.get_user(user.userId) for user in workspace.users]


def is_user_in_workspace(workspace_id: ObjectId, user_id: ObjectId):
    workspace = db.find_one(collection, _id=workspace_id)
    if workspace is not None:
        workspace = Workspace.from_dict(workspace)
    if user_id in workspace.users:
        return True
    return False


def are_users_in_workspace(workspace_id: ObjectId, user_ids: list):
    workspace = db.find_one(collection, _id=workspace_id)
    if workspace is not None:
        workspace = Workspace.from_dict(workspace)
    for user_id in user_ids:
        if user_id in workspace.users:
            return True
        else:
            return False

def get_teams(workspace_id: str) -> list:
    return Team.from_dict_list(db.find(collection=Collection.TEAM, workspaceId=ObjectId(workspace_id)))

def update_workspace_name(workspace_id: str, name: str):
    workspace = get_workspace(workspace_id=ObjectId(workspace_id))
    if workspace is None:
        abort(404, description="Workspace not found")
    workspace.name = name
    db.update(collection=collection, item=workspace)
    return get_workspace(workspace_id=ObjectId(workspace_id))

def delete_workspace(workspace_id: ObjectId) -> bool:
    db.delete(collection, id=workspace_id)
    return "ok"

def update_user_permissions(workspace_id: ObjectId, user_id: ObjectId, permissions: list):
    workspace = get_workspace(workspace_id=workspace_id)
    if workspace is None:
        abort(404, description="Workspace not found")
    permissions = permission_service.convert_to_workspace_permissions_enums(permissions)
    for i in range(len(workspace.users)):
        if user_id == workspace.users[i].userId:
            workspace.users[i].permissions = permissions
    db.update(collection=collection, item=workspace)
    return get_workspace(workspace_id=ObjectId(workspace_id))

def get_workspace_user(firebase_id:str, workspace_id: ObjectId):
    workspace = get_workspace(workspace_id=workspace_id)
    if workspace is None:
        abort(404, description="Workspace not found")
    user = users_service.get_user_by_firebase_id(firebase_id)
    for workspace_user in workspace.users:
        if workspace_user.userId == user.id:
            return workspace_user