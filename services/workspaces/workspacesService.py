from models.workspace import Workspace
import repositories.workspaceRepo as repo

def createWorkspace(workspace : Workspace) :
    return repo.insertWorkspace(workspace)

def getWorkspaceName(workspaceId):
    return repo.getWorkspaceName(workspaceId)