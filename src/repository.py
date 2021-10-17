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


def find(collection: Collection, **kwargs):
    if kwargs.get('id') is not None:
        kwargs['_id'] = ObjectId(kwargs['id'])
        del kwargs['id']

    return list(__get_collection(collection).find(kwargs))


def find_one(collection: Collection, **kwargs):
    if kwargs.get('id') is not None:
        kwargs['_id'] = ObjectId(kwargs['id'])
        del kwargs['id']

    return __get_collection(collection).find_one(kwargs)


def update(collection: Collection, item):
    query = {'_id': item['_id']}
    values = {'$set': item}
    __get_collection(collection).update_one(query, values)


def __get_collection(collection: Collection):
    client = mongo.MongoClient(f'{settings.MONGO_PROTOCOL}://{settings.MONGO_USER}:{settings.MONGO_PW}@{settings.MONGO_HOST}/{settings.MONGO_DEFAULT_DB}?retryWrites=true&w=majority')
    db = client.get_default_database()
    return db[collection.value]