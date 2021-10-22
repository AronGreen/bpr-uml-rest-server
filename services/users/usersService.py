from models.user import User
import repositories.usersRepo as repo

def addUser(user: User):
    dbUser = repo.getUserByFirebaseId(user.user_id)
    if dbUser == None:
        return repo.addUser(user)
    return dbUser["user_id"]