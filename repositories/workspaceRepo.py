from bson.objectid import ObjectId
from models.workspace import Workspace
import mongo as db
collection = db.Collection.WORKSPACE


def insertWorkspace(workspace: Workspace):
    return str(db.insert_one(workspace.__dict__, collection).inserted_id)


def getWorkspace(workspaceId: str):
    result = db.find_one(workspaceId, collection)
    if result is not None:
        return Workspace.from_dict(result)
    return


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'results': []}
    for x in db.find(None, collection=collection):
        result['results'].append(x)
    return result

def remove_user_from_workspace(user_id: str, workspace_id: str):
    workspace_dict = db.find_one(workspace_id, collection)
    workspace = Workspace.from_dict(workspace_dict)
    workspace.remove_user(user_id)
    if len(workspace.users) == 0:
        return "Not allowed to remove the last user"
    update_workspace_users(workspace)
    return "User removed"

def update_workspace_users(workspace: Workspace):
    db.update_document({'_id': ObjectId(workspace._id)}, {'users': workspace.users}, collection)