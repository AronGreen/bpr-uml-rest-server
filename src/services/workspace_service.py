from __future__ import annotations

from bpr_data.models.project import Project
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
from src.models.web_workspace_user import WebWorkspaceUser

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.WORKSPACE


def create_workspace(workspace: Workspace, firebase_id: str) -> Workspace:
    creator = users_service.get_user_by_firebase_id(firebase_id=firebase_id)
    workspace_user = WorkspaceUser(userId = creator.id, permissions=list(WorkspacePermission))
    workspace.users = [workspace_user]
    created_workspace = db.insert(collection, workspace)
    if created_workspace is not None:
        return Workspace.from_dict(created_workspace)


def get_workspace_for_user(workspace_id: ObjectId, firebase_id: str) -> Workspace:
    workspace = get_workspace(workspace_id=workspace_id)
    if workspace is None:
        abort(404, description="Workspace not found")
    user = users_service.get_user_by_firebase_id(firebase_id)
    for workspace_user in workspace.users:
        if workspace_user.userId == user.id:
            return workspace
    abort(403, description="User doesn't have access to the workspace")


def get_workspace_with_users_for_user(workspace_id: ObjectId, firebase_id: str) -> Workspace:
    workspace = get_workspace_with_users(workspace_id=workspace_id)
    if workspace is None:
        abort(404, description="Workspace not found")
    user = users_service.get_user_by_firebase_id(firebase_id)
    for workspace_user in workspace.users:
        if workspace_user.userId == user.id:
            return workspace
    abort(403, description="User doesn't have access to the workspace")


def get_workspace_with_users(workspace_id: ObjectId) -> Workspace:
    pipeline = [
        {'$match': {'_id': workspace_id}},
        __make_unwind_step('$users'),
        {
            '$lookup': {
                'from': 'user',
                'localField': 'users.userId',
                'foreignField': '_id',
                'as': 'users.user'
            }
        },
        __make_unwind_step('$users.user'),
        {'$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'users': {'$addToSet': '$users'}
        }}
    ]
    results = db.aggregate(collection=Collection.WORKSPACE,
                           pipeline=pipeline)
    if len(results) > 0:
        return Workspace.from_dict(results[0])


def __make_unwind_step(path: str, preserve_null_and_empty_arrays: bool = True) -> dict:
    return {
        '$unwind':
            {
                'path': path,
                'preserveNullAndEmptyArrays': preserve_null_and_empty_arrays
            }
    }


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
        if user.id not in [user.userId for user in workspace.users]:
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


def remove_workspace_user(workspace_id: ObjectId, user_id: ObjectId) -> bool:
    workspace = get_workspace(workspace_id)
    for user in workspace.users:
        if user.userId == user_id:
            workspace.users.remove(user)

            db.cleanup_relations(collection.PROJECT, 'users', {'userId': user_id})
            db.cleanup_relations(collection.TEAM, 'users', {'userId': user_id})

            return db.update(collection=collection, item=workspace)

    abort(400, description="user not in workspace")


def get_workspace_users(workspace_id: ObjectId, firebase_id: str) -> list:
    workspace = get_workspace_with_users(workspace_id)
    user = users_service.get_user_by_firebase_id(firebase_id=firebase_id)
    if user.id not in [user["userId"] for user in workspace.users]:
        abort(403, description="User does not have access to the workspace")
    if workspace.users is None:
        return list()
    return [WebWorkspaceUser.from_workspace_user(container) for container in workspace.users]


def are_users_in_workspace(workspace_id: ObjectId, user_ids: list):
    workspace = get_workspace(workspace_id)
    for user_id in user_ids:
        if user_id in [user.userId for user in workspace.users]:
            return True
        else:
            return False


def get_teams(workspace_id: str, firebase_id: str) -> list:
    get_workspace_for_user(workspace_id=workspace_id, firebase_id=firebase_id)
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


def get_workspace_user(firebase_id: str, workspace_id: ObjectId):
    workspace = get_workspace(workspace_id=workspace_id)
    if workspace is None:
        abort(404, description="Workspace not found")
    user = users_service.get_user_by_firebase_id(firebase_id)
    for workspace_user in workspace.users:
        if workspace_user.userId == user.id:
            return workspace_user
    abort(403, description="User not in workspace")
