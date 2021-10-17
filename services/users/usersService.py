from models.invitation import Invitation
from models.user import User
import util.emailValidator as emailValidator
import services.email.email as emailService
import services.workspaces.workspacesService as workspaceService
import repositories.usersRepo as repo

def inviteUser(invitation: Invitation):
    if(emailValidator.isValid(invitation.invitee_email_address)):
        workspaceName = workspaceService.getWorkspaceName(invitation.workspace_id)
        subject = "Diagramz invitation"
        message = "{} sent you an invitation on Diagramz to collaborate on {}".format(invitation.user_name, workspaceName)
        return emailService.send_email(invitation.invitee_email_address, subject, message)

def addUser(user: User):
    dbUser = repo.getUserByFirebaseId(user.user_id)
    if dbUser == None:
        return repo.addUser(user)
    return dbUser["user_id"]