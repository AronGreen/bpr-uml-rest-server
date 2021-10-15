from src.models.workspace import Workspace
import src.repository as db
collection = db.Collection.WORKSPACE


def create_workspace(workspace : Workspace) :
    return str(db.insert_one(workspace.__dict__, collection).inserted_id)


def get_workspace_ame(workspaceId):
    object = db.find_one_with_filter(workspaceId, {"_id": 0, "workspaceName": 1}, collection)
    return object["workspaceName"]


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'results': []}
    for x in db.find(None, collection=collection):
        result['results'].append(x)
    return result
