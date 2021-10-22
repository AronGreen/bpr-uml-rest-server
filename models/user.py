class User:
    def __init__(self, user_name, email, user_id):
        self.user_name = user_name
        self.email = email
        self.user_id = user_id

    def from_dict(theUser: dict):
        user_name = theUser["user_name"]
        email = theUser["email"]
        user_id = theUser["user_id"]
        return User(user_name, email, user_id)