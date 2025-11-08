import os

class Config:
    SECRET_KEY = 'B!1weNAt1T^%kvhUI*S^'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('postgresql://flask_login_6tjz_user:usFK1NDzJBS6baJktDwNAczd4N0wQze0@dpg-d47q6ummcj7s73did8e0-a/flask_login_6tjz')

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig
}
