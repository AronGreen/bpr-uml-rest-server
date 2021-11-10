from __future__ import annotations
from flask import abort

from bson import ObjectId

import src.repository as db
from src.models.project import Project, ProjectUser
import src.services.workspace_service as workspace_service
import src.services.users_service as users_service

collection = db.Collection.PROJECT


def get(project_id: str) -> Project:
    find_result = db.find_one(collection, id=project_id)
    if find_result is not None:
        return Project.from_dict(find_result)


def get_for_workspace(workspace_id: ObjectId) -> Project:
    find_result = db.find(collection, workspaceId=workspace_id)
    if find_result is not None:
        return Project.from_dict_list(find_result)


def create_project(title: str, workspaceId: ObjectId, creator_firebase_id: str) -> Project:
    workspace = workspace_service.get_workspace(workspace_id=workspaceId)
    user_id = users_service.get_user_by_firebase_id(firebase_id=creator_firebase_id).id
    if workspace is None:
        abort(404, description="Workspace not found")
    project = Project(
        _id=None,
        title=title,
        workspaceId=ObjectId(workspaceId),
        teams=list(),
        users=[user_id])
    insert_result = db.insert(collection, project)
    if insert_result is not None:
        return Project.from_dict(insert_result)


def update_project(project: Project) -> Project:
    update_result = db.update(collection, project)
    if update_result is not None:
        return Project.from_dict(update_result)


def delete_project(project_id: str | ObjectId) -> bool:
    return db.delete(collection, id=project_id)


def add_user(project_id: str, user_id: str, is_editor: bool) -> bool:
    user = ProjectUser(userId=ObjectId(user_id), isEditor=is_editor)
    return db.push(collection=collection, document_id=ObjectId(project_id), field_name='users', item=user)


def get_user_projects(workspace_id: str, user_id: ObjectId) -> list:
    return Project.from_dict_list(db.find(collection, workspaceId=ObjectId(workspace_id), users=user_id))
