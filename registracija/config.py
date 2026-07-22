from datetime import timedelta
from os import environ

class Configuration:

    SQLALCHEMY_DATABASE_URI = environ["DATABASE_URL"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = environ["JWT_KEY"]

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)