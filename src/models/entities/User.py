from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, fullname=None, email = None):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.email = email

    @classmethod
    def check_password(cls, hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)
    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)