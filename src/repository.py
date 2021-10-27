import json
from enum import Enum
import pymongo as mongo
from bson.objectid import ObjectId
from typing import Type, TypeVar

import settings
from src.models.mongo_document_base import MongoDocumentBase


# TDocument = TypeVar("TDocument", bound=MongoDocumentBase)


class Collection(Enum):
    APPLICATION_LOG = 'application_log'
    WORKSPACE = "workspace"
    USER = "user"
    TEAM = 'team'
    INVITATION = 'invitation'
    TESTING = 'testing'


def insert(collection: Collection, item: MongoDocumentBase):
    d = item.to_dict()
    if item.id is None:
        del d['_id']
    result = __get_collection(collection).insert_one(d)
    if result.acknowledged:
        return str(result.inserted_id)


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


def delete(collection: Collection, **kwargs):
    if kwargs.get('id') is not None:
        kwargs['_id'] = ObjectId(kwargs['id'])
        del kwargs['id']
    __get_collection(collection).delete_one(kwargs)


def update(collection: Collection, item: MongoDocumentBase):
    query = {'_id': item.id}
    values = {'$set': item.to_dict()}
    __get_collection(collection).update_one(query, values)


def push(collection: Collection, document_id: ObjectId, field_name: str, item):
    __get_collection(collection).update_one(
        {'_id': document_id},
        {'$push': {field_name: item}}
    )


def pull(collection: Collection, document_id: ObjectId, field_name: str, item):
    __get_collection(collection).update_one(
        {'_id': document_id},
        {'$pull': {field_name: item}}
    )


def __get_collection(collection: Collection):
    client = mongo.MongoClient(
        f'{settings.MONGO_PROTOCOL}://{settings.MONGO_USER}:{settings.MONGO_PW}@{settings.MONGO_HOST}/{settings.MONGO_DEFAULT_DB}?retryWrites=true&w=majority')
    db = client.get_default_database()
    return db[collection.value]
