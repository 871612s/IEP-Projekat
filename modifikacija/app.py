from flask import Flask
from pymongo import MongoClient
import redis
from os import environ
from config import Configuration

client = MongoClient(
    host=environ["MONGO_HOST"],
    port=27017,
    username=environ["MONGO_USER"],
    password=environ["MONGO_PASS"],
    authSource="admin"
)

database = client[environ["MONGO_DB"]]
assets = database["assets"]

redis_client = redis.Redis(
    host=environ["REDIS_HOST"],
    port=6379,
    decode_responses=True
)

application = Flask(__name__)
application.config.from_object(Configuration)

import routes

if __name__ == "__main__":
    application.run()