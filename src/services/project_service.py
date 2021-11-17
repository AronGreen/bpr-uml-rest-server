from __future__ import annotations
from flask import abort
from src.util import list_util

from bson import ObjectId

import src.repository as db
from src.models.project import Project, ProjectUser
import src.services.workspace_service as workspace_service
import src.services.users_service as users_service

collection = db.Collection.PROJECT


def get(project_id: str) -> Project:
    find_result = db.find_one(collection, id=project_id)
    if find_result is not None:
        project = Project.from_dict(find_result)
        project.users = ProjectUser.from_dict_list(project.users)
        return project


def get_for_workspace(workspace_id: ObjectId) -> Project:
    find_result = db.find(collection, workspaceId=workspace_id)
    if find_result is not None:
        projects = Project.from_dict_list(find_result)
        for project in projects:
           project.users = ProjectUser.from_dict_list(project.users)
        return project 


def create_project(title: str, workspaceId: ObjectId, creator_firebase_id: str) -> Project:
    workspace = workspace_service.get_workspace(workspace_id=ObjectId(workspaceId))
    user_id = users_service.get_user_by_firebase_id(firebase_id=creator_firebase_id).id
    if workspace is None:
        abort(404, description="Workspace not found")
    project = Project(
        _id=None,
        title=title,
        workspaceId=ObjectId(workspaceId),
        teams=list(),
        users=[ProjectUser(userId=user_id, isEditor=True)])
    insert_result = db.insert(collection, project)
    if insert_result is not None:
        return Project.from_dict(insert_result)


def update_project(project: Project) -> Project:
    update_result = db.update(collection, project)
    if update_result is not None:
        return Project.from_dict(update_result)


def delete_project(project_id: str | ObjectId) -> bool:
    return db.delete(collection, id=project_id)


def add_users(project_id: str, users: list) -> Project:
    project = get(project_id=project_id)
    list_util.ensure_no_duplicates(users, "userId")
    if not workspace_service.are_users_in_workspace(workspace_id=project.workspaceId, user_ids=[user.userId for user in users]):
        abort(400)
    for user in users:
        for project_user in project.users:
            if user.userId == project_user.userId:
                abort(400)
    items = ProjectUser.as_dict_list(users)
    db.push_list(collection=collection, document_id=ObjectId(project_id), field_name='users', items=items)
    return get(project_id=project_id)


def get_user_projects(workspace_id: str, user_id: ObjectId) -> list:
    return Project.from_dict_list(db.find(collection=collection, nested_conditions={'users.userId': user_id}, workspaceId=ObjectId(workspace_id)))