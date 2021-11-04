from __future__ import annotations

from bson import ObjectId

import src.repository as db
from src.models.project import Project

collection = db.Collection.PROJECT


def get(project_id: str) -> Project:
    find_result = db.find_one(collection, id=project_id)
    if find_result is not None:
        return Project.from_dict(find_result)


def get_for_workspace(workspace_id: ObjectId) -> Project:
    find_result = db.find(collection, workspaceId=workspace_id)
    if find_result is not None:
        return Project.from_dict_list(find_result)


def create_project(title: str, workspaceId: ObjectId) -> Project:
    project = Project(
        _id=None,
        title=title,
        workspaceId=workspaceId,
        projectTeams=list(),
        projectUsers=list())
    insert_result = db.insert(collection, project)
    if insert_result is not None:
        return Project.from_dict(insert_result)


def update_project(project: Project) -> Project:
    update_result = db.update(collection, project)
    if update_result is not None:
        return Project.from_dict(update_result)


def delete_project(project_id: str | ObjectId) -> bool:
    return db.delete(collection, id=project_id)
