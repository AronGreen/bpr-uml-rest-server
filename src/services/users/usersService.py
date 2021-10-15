from models.invitation import Invitation
import util.emailValidator as emailValidator
import services.email.email as emailService
import services.workspaces.workspacesService as workspaceService
import repositories.usersRepo as repo

def inviteUser(invitation: Invitation):
    if(emailValidator.isValid(invitation.inviteeEmailAddress)):
        workspaceName = workspaceService.getWorkspaceName(invitation.workspaceId)
        invitorName = getUserName(invitation.invitorId)
        subject = "Diagramz invitation"
        message = "{} sent you an invitation on Diagramz to collaborate on {}".format(invitorName, workspaceName)
        return emailService.send_email(invitation.inviteeEmailAddress, subject, message)

def getUserName(userId):
    return repo.getUserName(userId)

def addUser(user):
    return repo.addUser(user)