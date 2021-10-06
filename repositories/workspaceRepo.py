import mongo as db

def insertWorkspace(workspace_json):
    return str(db.insert_one(workspace_json, db.Collection.WORKSPACE).inserted_id)
