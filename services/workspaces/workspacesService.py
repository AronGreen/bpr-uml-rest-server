import repositories.workspaceRepo as repo

def createWorkspace(workspace_json) :
    return repo.insertWorkspace(workspace_json)