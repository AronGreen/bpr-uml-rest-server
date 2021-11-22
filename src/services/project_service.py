from __future__ import annotations
from flask import abort
from bson import ObjectId

from bpr_data.repository import Repository, Collection
from bpr_data.models.project import Project, ProjectUser

from src.util import list_util
import src.services.workspace_service as workspace_service
import src.services.users_service as users_service
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.PROJECT


def get(project_id: str) -> Project:
    # find_result = db.find_one(collection, id=project_id)
    # if find_result is not None:
    #     project = Project.from_dict(find_result)
    #     project.users = ProjectUser.from_dict_list(project.users)
    #     return project
    return __get_full_project(project_id)


def get_for_workspace(workspace_id: ObjectId) -> Project:
    find_result = db.find(collection, workspaceId=workspace_id)
    if find_result is not None:
        projects = Project.from_dict_list(find_result)
        for project in projects:
            project.users = ProjectUser.from_dict_list(project.users)
        return projects


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
    if not workspace_service.are_users_in_workspace(workspace_id=project.workspaceId,
                                                    user_ids=[user.userId for user in users]):
        abort(400)
    for user in users:
        for project_user in project.users:
            if user.userId == project_user.userId:
                abort(400)
    items = ProjectUser.as_dict_list(users)
    db.push_list(collection=collection, document_id=ObjectId(project_id), field_name='users', items=items)
    return get(project_id=project_id)


def get_user_projects(workspace_id: str, user_id: ObjectId) -> list:
    return Project.from_dict_list(
        db.find(collection=collection, nested_conditions={'users.userId': user_id}, workspaceId=ObjectId(workspace_id)))


def replace_users(project_id: str | ObjectId, users: list) -> Project:
    project = get(project_id=project_id)
    for user in users:
        user['userId'] = ObjectId(user['userId'])
    project_users = ProjectUser.from_dict_list(users)
    project.users = project_users
    db.update(Collection.PROJECT, project)
    return __get_full_project(project_id)


def __get_full_project(project_id: str | ObjectId) -> Project:
    pipeline = [
        {'$match': {'_id': ObjectId(project_id)}},
        __make_unwind_step('$users'),
        __make_unwind_step('$teams'),
        {
            '$lookup': {
                'from': 'user',
                'localField': 'users.userId',
                'foreignField': '_id',
                'as': 'users.user'
            }
        },
        {
            '$lookup': {
                'from': 'team',
                'localField': 'teams.teamId',
                'foreignField': '_id',
                'as': 'teams.team'
            }
        },
        __make_unwind_step('$users.user'),
        __make_unwind_step('$teams.team'),
        {'$group': {
            '_id': '$_id',
            'title': {'$first': '$title'},
            'workspaceId': {'$first': '$workspaceId'},
            'users': {'$addToSet': '$users'},
            'teams': {'$addToSet': '$teams'}
        }}
    ]
    results = db.aggregate(collection=Collection.PROJECT,
                           pipeline=pipeline,
                           return_type=Project)
    if len(results) > 0:
        return results[0]


# TODO: move to util module in bpr_data?
def __make_unwind_step(path: str, preserve_null_and_empty_arrays: bool = True) -> dict:
    return {
        '$unwind':
            {
                'path': path,
                'preserveNullAndEmptyArrays': preserve_null_and_empty_arrays
            }
    }
