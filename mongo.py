from datetime import datetime
from enum import Enum
import pymongo as mongo
import settings
import json

class Collection(Enum):
    DEBUG_LOG = "debug_log"
    WORKSPACE = "workspace"


def debug_log(content: dict, note: str):
    """
    Storage for debug log
    """
    item = {
        'date': str(datetime.now()),
        'note': note,
        'content':json.dumps(content)
    }
    insert_one(item, Collection.DEBUG_LOG)


def insert_one(item, collection: Collection):
    col = __get_collection(collection)
    return col.insert_one(item)


def __get_collection(collection: Collection):
    client = mongo.MongoClient(f"{settings.MONGO_PROTOCOL}://{settings.MONGO_USER}:{settings.MONGO_PW}@{settings.MONGO_HOST}/{settings.MONGO_DEFAULT_DB}?retryWrites=true&w=majority")
    db = client.get_default_database()
    return db[collection.value]

