from extensions import db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(256), nullable=False)
    surname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, forename, surname, email, password, role, wallet = None):
        self.forename = forename
        self.surname = surname
        self.email = email
        self.password = password
        self.role = role
        
    def __repr__(self):
        return f"<User({self.id}){self.forename}, {self.surname}, {self.email}, {self.role}>"

    def to_dict(self):
        return {
            "forename": self.forename,
            "surname": self.surname,
            "email": self.email,
            "role": self.role
        }