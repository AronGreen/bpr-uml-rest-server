from __future__ import annotations

from bson import ObjectId
from flask import g, abort

from bpr_data.repository import Repository, Collection
from bpr_data.models.invitation import Invitation
from bpr_data.models.user import User
from bpr_data.models.workspace import Workspace

import src.util.email_utils as email
import src.services.email_service as email_service
import src.services.users_service as users_service
import src.services.invitation_service as invitation_service
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.WORKSPACE


def create_workspace(workspace: Workspace) -> Workspace:
    creator = User.from_dict(db.find_one(Collection.USER, firebaseId=g.firebase_id))
    workspace.users = [creator.id]
    created_workspace = db.insert(collection, workspace)
    if created_workspace is not None:
        return Workspace.from_dict(created_workspace)


def get_workspace(workspace_id: ObjectId) -> Workspace:
    find_result = db.find_one(collection, _id=workspace_id)
    if find_result is not None:
        return Workspace.from_dict(find_result)


def get_user_workspaces(firebase_id: str) -> list:
    # TODO: filter so only current users workspaces are present
    user = users_service.get_user_by_firebase_id(firebase_id)
    find_result = db.find(collection=collection, users=user.id)
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
            item=user_id
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
    if workspace.users is None:
        return list()
    return [users_service.get_user(user_id) for user_id in workspace.users]


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
