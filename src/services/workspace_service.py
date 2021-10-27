from src.models.invitation import Invitation
from src.models.workspace import Workspace
import src.repository as db
import src.util.email_utils as email
import src.services.email_service as email_service
import src.services.users_service as users_service
import src.services.invitation_service as invitation_service

collection = db.Collection.WORKSPACE


def create_workspace(workspace: Workspace):
    return db.insert(collection, workspace)


def get_workspace(workspace_id):
    return Workspace.from_dict(db.find_one(collection, _id=workspace_id))


def get_workspace_name(workspace_id):
    return get_workspace(workspace_id).name


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'data': Workspace.from_dict_list(db.find(collection))}
    return result


def invite_user(invitation: Invitation):
    if email.is_valid(invitation.invitee_email_address):
        user = users_service.get_user_by_email_address(invitation.invitee_email_address)
        workspace = get_workspace(invitation.workspace_id)
        if workspace is None:
            return
        if user is None:
            subject = "Diagramz invitation"
            message = "{} sent you an invitation on Diagramz to collaborate on {}".format(g.user_name,
                                                                                          workspace.workspace_name)
            email_service.send_email(invitation.invitee_email_address, subject, message)
        invitation_service.add_invitation(invitation)
        return "Invitation sent"
    return "Invalid email"


def respond_to_invitation(invitation_id, accepted):
    return_text = ""
    if accepted:
        invitation = invitation_service.get_invitation(invitation_id)
        if invitation is not None:
            user = users_service.get_user_by_email_address(invitation.invitee_email_address)
            workspace = get_workspace(invitation.workspace_id)
            if user is not None and workspace is not None:
                workspace.add_user(user["user_id"])
                add_workspace_user(invitation.workspace_id, user.user_id)
                return_text = "User added"
        else:
            return_text = "Invitation not found"
    else:
        return_text = "Invitation declined"
    invitation_service.delete_invitation(invitation_id)
    return return_text


def add_workspace_user(workspace_id, user_id):
    db.push(
        collection=db.Collection.WORKSPACE,
        document_id=workspace_id,
        field_name='users',
        item=user_id
    )


def remove_workspace_user(workspace_id, user_id):
    db.pull(
        collection=db.Collection.WORKSPACE,
        document_id=workspace_id,
        field_name='users',
        item=user_id
    )
