from __future__ import annotations

from bson import ObjectId

import src.repository as db
from src.models.project import Project, ProjectUser

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
        teams=list(),
        users=list())
    insert_result = db.insert(collection, project)
    if insert_result is not None:
        return Project.from_dict(insert_result)


def update_project(project: Project) -> Project:
    update_result = db.update(collection, project)
    if update_result is not None:
        return Project.from_dict(update_result)


def delete_project(project_id: str | ObjectId) -> bool:
    return db.delete(collection, id=project_id)


def add_user(project_id: str, user_id: str, is_editor: bool):
    user = ProjectUser(userId=ObjectId(user_id), isEditor=is_editor)
    return db.push(collection=collection, document_id=ObjectId(project_id), field_name='users', item=user)


def get_user_projects(workspace_id: str, user_id: ObjectId) -> list:
    projects = Project.from_dict_list(db.find(collection, workspaceId=workspace_id))

    user_projects = list()
    for project in projects:
        for user in project.users:
            if user['userId'] == user_id:
                user_projects.append(project)
                break

    return user_projects
