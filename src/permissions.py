from enum import Enum, auto

from bpr_data.models.mongo_document_base import SerializableObject


class WorkspacePermission(str, Enum):
    MANAGE_TEAMS = "MANAGE_TEAMS"
    MANAGE_PERMISSIONS = "MANAGE_PERMISSIONS"
    MANAGE_WORKSPACE = "MANAGE_WORKSPACE"
    MANAGE_USERS = "MANAGE_USERS"

class ProjectPermission(str, Enum):
    MANAGE_PROJECTS = "MANAGE_PROJECTS"