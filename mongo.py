from datetime import datetime
import pymongo as mongo
import settings



def debug_store(content):
    item = {
        'date': datetime.now,
        'content':content
    }
    __insert_one("debug_store", item)


def __insert_one(collection, item):
    col = __get_collection(collection)
    col.insert_one(item)


def __get_collection(collection):
    client = mongo.MongoClient(
        host=settings.MONGO_HOST, 
        port=settings.MONGO_PORT)
    con = client[settings.MONGO_DB]
    return con[collection]

