from bson import ObjectId

import src.repository as db
from src.models.diagram import Diagram

collection = db.Collection.DIAGRAM


def create_diagram(title: str, projectId: str) -> Diagram:
    insert_result = db.insert(collection, Diagram(_id=None, title=title, projectId=ObjectId(projectId), models=list()))
    if insert_result is not None:
        return Diagram.from_dict(insert_result)


