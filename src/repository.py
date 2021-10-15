from enum import Enum
import pymongo as mongo
import settings
from bson.objectid import ObjectId


class Collection(Enum):
    DEBUG_LOG = "debug_log"
    WORKSPACE = "workspace"
    USER = "user"
    APPLICATION_LOG = 'application_log'
    MATE_TEST = 'mate_test'


def insert(collection: Collection, item):
    return __get_collection(collection).insert_one(item)


def find(collection: Collection, **filter):
    return __get_collection(collection).find(filter)


def find_one(collection: Collection, **filter):
    return __get_collection(collection).find_one(filter)


def __get_collection(collection: Collection):
    client = mongo.MongoClient(f'{settings.MONGO_PROTOCOL}://{settings.MONGO_USER}:{settings.MONGO_PW}@{settings.MONGO_HOST}/{settings.MONGO_DEFAULT_DB}?retryWrites=true&w=majority')
    db = client.get_default_database()
    return db[collection.value]