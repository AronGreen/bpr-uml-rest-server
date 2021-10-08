from pymongo import collection
from models.workspace import Workspace
import mongo as db
collection = db.Collection.WORKSPACE

def insertWorkspace(workspace: Workspace):
    return str(db.insert_one(workspace.__dict__, collection).inserted_id)

def getWorkspaceName(workspaceId: str):
    object = db.find_one_with_filter( workspaceId, { "_id": 0, "workspaceName":1 }, collection )
    return object["workspaceName"]