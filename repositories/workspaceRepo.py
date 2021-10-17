from models.workspace import Workspace
import mongo as db
collection = db.Collection.WORKSPACE


def insertWorkspace(workspace: Workspace):
    return str(db.insert_one(workspace.__dict__, collection).inserted_id)


def getWorkspaceName(workspaceId: str):
    object = db.find_one_with_filter( workspaceId, { "_id": 0, "workspace_name":1 }, collection )
    return object["workspace_name"]


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'results': []}
    for x in db.find(None, collection=collection):
        result['results'].append(x)
    return result
