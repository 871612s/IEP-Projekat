from os import environ

class Configuration:
    JWT_SECRET_KEY = environ["JWT_KEY"]