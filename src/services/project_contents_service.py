from __future__ import annotations

from typing import Union, List

from bpr_data.models.diagram import Diagram
from bpr_data.models.model import Model
from bpr_data.models.project import Project
from bpr_data.repository import Repository, Collection
from bson import ObjectId

import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.PROJECT

MongoId = Union[ObjectId, str]


def get_project_contents(project_id: MongoId):
    project = db.find_one(Collection.PROJECT, return_type=Project, id=project_id)
    diagrams = db.find(Collection.DIAGRAM, return_type=Diagram, projectId=ObjectId(project_id))
    models = db.find(Collection.MODEL, return_type=Model, projectId=ObjectId(project_id))

    folders = {
        '_id': str(project.id),
        'name': project.title,
        'items': list()
    }

    # TODO: some of this can be handled in aggregation pipelines
    # should be more performant.
    for folder in project.folders:
        folders['items'].append({
            'path': folder,
            'type': 'folder',
            'name': folder.strip('/').split('/')[-1],
            'id': None
        })

    for diagram in diagrams:
        folders['items'].append({
            'path': diagram.path,
            'type': 'diagram',
            'name': diagram.title,
            'id': str(diagram.id)
        })

    for model in models:
        name = 'unnamed'
        name_attr = next((x for x in model.attributes if x['kind'] == 'name'), None)
        if name_attr is not None:
            name = name_attr['value']
        else:
            text_attr = next((x for x in model.attributes if x['kind'] == 'text'), None)
            if text_attr is not None:
                name = text_attr['value'][:10]

        folders['items'].append({
            'path': model.path,
            'type': 'model',
            'name': name,
            'id': str(model.id)
        })
    return folders


def create_folder(projectId: MongoId, path: str) -> bool:
    path_items = __get_path_parts(path)
    return db.push_list(Collection.PROJECT, document_id=ObjectId(projectId), field_name='folders', items=path_items)


def delete_folder(project_id: MongoId, path: str) -> bool:
    # path = __slash(path)
    project = db.find_one(Collection.PROJECT, return_type=Project, id=project_id)
    diagrams = db.find(Collection.DIAGRAM, return_type=Diagram, projectId=ObjectId(project_id))
    models = db.find(Collection.MODEL, return_type=Model, projectId=ObjectId(project_id))

    block_delete = any(d for d in diagrams if d.path.startswith(path)) \
        or any(m for m in models if m.path.startswith(path))
    if block_delete:
        return False

    # if deletion is not blocked by this point delete folder and any sub-folders
    to_delete = [f for f in project.folders if f.startswith(path)]
    for item in to_delete:
        db.pull(Collection.PROJECT, document_id=ObjectId(project_id), field_name='folders', item=item)
    return True

#
# def __slash(string:str) -> str:
#     if not string.startswith('/'):
#         string = '/' + string
#     if not string.endswith('/'):
#         string = string + '/'
#     return string


def __get_path_parts(string: str) -> List[str]:
    def get_path_rec(full_path: list, current_index: int, acc: list):
        if len(full_path) == current_index:
            return acc
        sub_list = full_path[:current_index + 1]
        acc.append('/' + '/'.join([f'{s}' for s in sub_list]) + '/')
        return get_path_rec(full_path, current_index + 1, acc)

    return get_path_rec(string.strip('/').split('/'), 0, list())
