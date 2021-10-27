from enum import Enum
import pymongo as mongo
import settings
from bson.objectid import ObjectId

"""
insert
insert_many
update
update_many
remove
remove_many
find

count
"""

class Collection(Enum):
    DEBUG_LOG = "debug_log"
    WORKSPACE = "workspace"
    USER = "user"
    APPLICATION_LOG = 'application_log'
    INVITATION = 'invitation'
    TEAM = 'team'
    MATE_TEST = 'mate_test'


def insert_one(item, collection: Collection):
    col = __get_collection(collection)
    return col.insert_one(item)


def find_one(id: str, collection: Collection):
    col = __get_collection(collection)
    return col.find_one( { "_id": ObjectId(id) } )

# TODO: look into **kwargs in stead of filter
def find_one_with_filter(id: str, filter: dict, collection: Collection):
    col = __get_collection(collection)
    return col.find_one( { "_id": ObjectId(id) }, filter )

def find_from_query(query: dict, collection: Collection):
    col = __get_collection(collection)
    return col.find(query)

def find(filter: dict, collection: Collection):
    col = __get_collection(collection)
    if filter is None:
        return col.find()
    return col.find(filter)

def delete_document(id:str, collection: Collection):
    col = __get_collection(collection)
    col.delete_one({"_id": ObjectId(id)})

def update_document(condition: dict, fields_to_update: dict, collection: Collection):
    col = __get_collection(collection)
    col.update_one(condition, {"$set": fields_to_update})

def __get_collection(collection: Collection):
    client = mongo.MongoClient(f'{settings.MONGO_PROTOCOL}://{settings.MONGO_USER}:{settings.MONGO_PW}@{settings.MONGO_HOST}/{settings.MONGO_DEFAULT_DB}?retryWrites=true&w=majority')
    db = client.get_default_database()
    return db[collection.value]

