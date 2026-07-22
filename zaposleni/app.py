from pymongo import MongoClient
from os import environ
from flask import Flask
from config import Configuration
from flask_jwt_extended import JWTManager
import redis

redis_client = redis.Redis(
    host=environ["REDIS_HOST"],
    port=6379,
    decode_responses=True
)

client = MongoClient(
    host=environ["MONGO_HOST"],
    port=27017,
    username=environ["MONGO_USER"],
    password=environ["MONGO_PASS"],
    authSource="admin"
)

database = client[environ["MONGO_DB"]]
assets = database["assets"]

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager()
jwt.init_app(application)

import routes

if __name__ == "__main__":
    application.run()