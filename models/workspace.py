from models.workspace_user import WorkspaceUser


class Workspace:
  def __init__(self, creator_id, workspace_name, users=[], id=None):
    self.creator_id = creator_id
    self.workspace_name = workspace_name
    self.users = users
    if id!=None: 
      self._id = id

  def set_users(self, users: list):
    self.users = users

  def add_user(self, user_id: str):
    for id in self.users:
      if id == user_id:
        return
    self.users.append(user_id)

  def remove_user(self, user_id: str):
    for user in self.users:
      if(user == user_id):
        self.users.remove(user)

  def from_dict(the_workspace: dict):
    creator_id = the_workspace["creator_id"]
    workspace_name = the_workspace["workspace_name"]
    if "users" in the_workspace:
      users = the_workspace["users"]
    _id = the_workspace["_id"]
    return Workspace(creator_id, workspace_name, users, _id)