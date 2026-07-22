from flask import Flask
from config import Configuration
from flask_jwt_extended import JWTManager
from extensions import db, jwt, migrate

application = Flask(__name__)
application.config.from_object(Configuration)

db.init_app(application)
jwt.init_app(application)
migrate.init_app(application, db)
import routes
from seed import seed

with application.app_context():
    db.create_all()
    seed()

if __name__ == "__main__":
    application.run(debug=True)