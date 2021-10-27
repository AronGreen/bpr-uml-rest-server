from models.workspace import Workspace
from models.workspace_user import WorkspaceUser
import repositories.workspaceRepo as repo
import repositories.invitationRepo as invitationRepo
import repositories.usersRepo as usersRepo
import services.email.email as emailService
from models.invitation import Invitation
import util.emailValidator as emailValidator
from flask import g


def createWorkspace(workspace: Workspace):
    return repo.insertWorkspace(workspace)


def getWorkspace(workspaceId):
    return repo.getWorkspace(workspaceId)


def get_user_workspaces(user_id: str):
    return repo.get_user_workspaces(user_id=user_id)
    
def remove_user_from_workspace(user_id: str, workspace_id: str):
    return repo.remove_user_from_workspace(user_id, workspace_id)

def inviteUser(invitation: Invitation):
    if(emailValidator.isValid(invitation.invitee_email_address)):
        user = usersRepo.getUserByEmailAddress(invitation.invitee_email_address)
        workspace = getWorkspace(invitation.workspace_id)
        if workspace is None:
            return
        if user is None:
            subject = "Diagramz invitation"
            message = "{} sent you an invitation on Diagramz to collaborate on {}".format(g.user_name, workspace.workspace_name)
            emailService.send_email(invitation.invitee_email_address, subject, message)
        invitationRepo.addInvitation(invitation)
        return "Invitation sent"
    return "Invalid email"

def respond_to_invitation(invitation_id, accepted):
    if accepted:
        invitation = invitationRepo.get_invitation(invitation_id)
        if invitation is not None:
            user = usersRepo.getUserByEmailAddress(invitation.invitee_email_address)
            workspace = repo.getWorkspace(invitation.workspace_id)
            if user is not None and workspace is not None:
                workspace.add_user(user["user_id"])
                repo.update_workspace_users(workspace)
                return_text = "User added"
        else:
            return_text="Invitation not found"
    else:
        return_text = "Invitation declined"
    invitationRepo.delete_invitation(invitation_id)
    return return_text
