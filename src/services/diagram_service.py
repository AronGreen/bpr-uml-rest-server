from bson import ObjectId

import src.repository as db
from src.models.diagram import Diagram

collection = db.Collection.DIAGRAM


def create_diagram(title: str, projectId: str, path: str) -> Diagram:
    if path is None:
        path = ''
    insert_result = db.insert(collection, Diagram(_id=None, title=title, projectId=ObjectId(projectId), models=list(), path=path))
    if insert_result is not None:
        return Diagram.from_dict(insert_result)


