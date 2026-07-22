from roles import Roles
from models import User
from extensions import db
import bcrypt
def seed():

    user = User.query.filter(
        User.email=="onlymoney@gmail.com"
    ).first()

    if user is None:

        user = User(
        forename="Scrooge",
        surname="McDuck",
        email="onlymoney@gmail.com",
        password=bcrypt.hashpw("evenmoremoney".encode(),bcrypt.gensalt()).decode(),
        role=Roles.DIRECTOR
        )

        db.session.add(user)
        db.session.commit()