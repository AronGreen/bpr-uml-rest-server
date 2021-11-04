from flask import g

from src.models.invitation import Invitation
from src.models.workspace import Workspace
import src.repository as db
import src.util.email_utils as email
import src.services.email_service as email_service
import src.services.users_service as users_service
import src.services.invitation_service as invitation_service

collection = db.Collection.WORKSPACE


def create_workspace(workspace: Workspace) -> Workspace:
    created_workspace = db.insert(collection, workspace)
    if created_workspace is not None:
        return Workspace.from_dictionary(created_workspace)


def get_workspace(workspace_id: str) -> Workspace:
    find_result = db.find_one(collection, id=workspace_id)
    if find_result is not None:
        return Workspace.from_dict(find_result)


def get_workspace_name(workspace_id) -> str:
    return get_workspace(workspace_id).name


def get_user_workspaces(user_id: str) -> list:
    # TODO: filter so only current users workspaces are present
    find_result = db.find(collection)
    if find_result is not None:
        return Workspace.from_dict_list(find_result)


# TODO: move to invitation service
def invite_user(invitation: Invitation) -> str:
    if email.is_valid(invitation.inviteeEmailAddress):
        user = users_service.get_user_by_email_address(invitation.inviteeEmailAddress)
        workspace = get_workspace(invitation.workspaceId.__str__())
        if workspace is None:
            return "Workspace does not exist"
        if user is None:
            subject = "Diagramz invitation"
            message = "{} sent you an invitation on Diagramz to collaborate on {}".format(g.user_name,
                                                                                          workspace.workspaceName)
            email_service.send_email(invitation.inviteeEmailAddress, subject, message)
        invitation_service.add_invitation(invitation)
        return "Invitation sent"
    return "Invalid email"


# TODO: move to invitation service
def respond_to_invitation(invitation_id, accepted) -> str:
    return_text = ""
    if accepted:
        invitation = invitation_service.get_invitation(invitation_id)
        if invitation is not None:
            user = users_service.get_user_by_email_address(invitation.inviteeEmailAddress)
            workspace = get_workspace(invitation.workspaceId.__str__())
            if user is not None and workspace is not None:
                workspace.add_user(user["user_id"])
                add_workspace_user(invitation.workspaceId, user.user_id)
                return_text = "User added"
        else:
            return_text = "Invitation not found"
    else:
        return_text = "Invitation declined"
    invitation_service.delete_invitation(invitation_id)
    return return_text


def add_workspace_user(workspace_id, user_id) -> bool:
    return db.push(
        collection=db.Collection.WORKSPACE,
        document_id=workspace_id,
        field_name='users',
        item=user_id
    )


def remove_workspace_user(workspace_id, user_id) -> bool:
    return db.pull(
        collection=db.Collection.WORKSPACE,
        document_id=workspace_id,
        field_name='users',
        item=user_id
    )
