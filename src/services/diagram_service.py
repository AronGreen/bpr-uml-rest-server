from bson import ObjectId

from bpr_data.repository import Repository, Collection
from bpr_data.models.diagram import Diagram

import settings

db = Repository.get_instance(
    protocol=settings.MONGO_PROTOCOL,
    default_db=settings.MONGO_DEFAULT_DB,
    pw=settings.MONGO_PW,
    host=settings.MONGO_HOST,
    user=settings.MONGO_USER)

collection = Collection.DIAGRAM


def create_diagram(title: str, projectId: str, path: str) -> Diagram:
    if path is None:
        path = ''
    insert_result = db.insert(collection, Diagram(_id=None, title=title, projectId=ObjectId(projectId), models=list(), path=path))
    if insert_result is not None:
        return Diagram.from_dict(insert_result)


