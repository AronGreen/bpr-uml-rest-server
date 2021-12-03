from bpr_data.models.permission import WorkspacePermission

def convert_to_workspace_permissions_enums(permissions: list):
    enum_permissions = []
    for permission in permissions: 
        enum_permissions.append(WorkspacePermission(permission))
    return enum_permissions