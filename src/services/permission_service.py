from bson import ObjectId
import src.services.workspace_service as workspace_service
import src.services.project_service as project_service
from flask import abort


def check_permissions(firebase_id: str, workspace_id: ObjectId, permissions: list):
    workspace_user = workspace_service.get_workspace_user(firebase_id=firebase_id, workspace_id=workspace_id)
    if workspace_user is None:
        abort(403, description="Missing permissions")
    if all(item in workspace_user.permissions for item in permissions):
        return True
    abort(403, description="Missing permissions")


def check_manage_project(firebase_id: str, project_id: ObjectId):
    user=project_service.get_project_user(firebase_id=firebase_id, project_id=project_id)
    if user.isProjectManager is False:
        abort(403, "Missing permissions")


def check_is_editor(firebase_id: str, project_id: ObjectId):
    user=project_service.get_project_user(firebase_id=firebase_id, project_id=project_id)
    if user.isEditor is False:
        abort(403, "Missing permissions")