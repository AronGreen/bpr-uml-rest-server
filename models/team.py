class Team:
  def __init__(self, team_name, workspace_id, users=[], id=None):
    self.team_name = team_name
    self.workspace_id = workspace_id
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

  def from_dict(the_team: dict):
    team_name = the_team["team_name"]
    workspace_id = the_team["workspace_id"]
    if "users" in the_team:
      users = the_team["users"]
    _id = the_team["_id"]
    return Team(team_name, workspace_id, users, _id)