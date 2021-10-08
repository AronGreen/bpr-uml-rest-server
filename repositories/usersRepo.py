from pymongo import collection
import mongo as db

collection = db.Collection.USER

def getUserName(userId):
    return db.find_one_with_filter( userId, { "userName": 1 }, collection)["userName"]
    
def addUser(user):
    return str(db.insert_one(user.__dict__, collection).inserted_id)
