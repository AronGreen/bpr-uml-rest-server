import mongo as db

def insertWorkspace(workspace_json):
    return str(db.get_collection("workspace").insert_one(workspace_json).inserted_id)
