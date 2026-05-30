from models.user_model import UserModel


def login(username, password):
    return UserModel.authenticate(username, password)
