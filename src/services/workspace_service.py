from src.models.workspace import Workspace
import src.repository as db

collection = db.Collection.WORKSPACE


def create_workspace(workspace: Workspace):
    return str(db.insert(collection, workspace.__dict__,).inserted_id)


def get_workspace_name(workspace_id):
    object = db.find_one(collection, _id=workspace_id)
    return object["workspaceName"]


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'results': []}
    for x in db.find(collection):
        result['results'].append(x)
    return result
