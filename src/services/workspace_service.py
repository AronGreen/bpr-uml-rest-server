from src.models.workspace import Workspace
import src.repository as db

collection = db.Collection.WORKSPACE


def create_workspace(workspace: Workspace):
    return str(db.insert(collection, workspace).inserted_id)


def get_workspace(workspace_id):
    return Workspace.from_dict(db.find_one(collection, _id=workspace_id))


def get_workspace_name(workspace_id):
    return get_workspace(workspace_id).name


def get_user_workspaces(user_id: str):
    # TODO: filter so only current users workspaces are present
    result = {'results': Workspace.from_dict_list(db.find(collection))}
    return result


