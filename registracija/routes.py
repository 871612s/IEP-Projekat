from flask import request,jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 
from email_validator import validate_email, EmailNotValidError
from app import application
from roles import Roles
from models import User
from extensions import db
import bcrypt
from web3 import Web3
import re

EMAIL_TLD_RE = re.compile(r"\.[A-Za-z]{2,}$")

@application.route("/register", methods=["POST"])
def register():

    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    
    if len(forename) == 0:
        return jsonify(message="Field forename is missing."), 400
    if len(surname) == 0:
        return jsonify(message="Field surname is missing."), 400
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
        
    try:
        validate_email(email, check_deliverability=False)
        if not EMAIL_TLD_RE.search(email):
            raise EmailNotValidError()
    except EmailNotValidError:
        return jsonify(message="Invalid email."), 400
    
    if len(password) < 8 or len(password) > 256:
        return jsonify(message="Invalid password."), 400

    if User.query.filter(User.email == email).first():
        return jsonify(message="Email already exists."), 400
    
    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()
    
    user = User(
        forename=forename,
        surname=surname,
        email=email,
        password=password_hash,
        role=Roles.EMPLOYEE
    )
    
    db.session.add(user)
    db.session.commit()
    
    return "", 200


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400
    
    try:
        validate_email(email, check_deliverability=False)
        if not EMAIL_TLD_RE.search(email):
            raise EmailNotValidError()
    except EmailNotValidError:
        return jsonify(message="Invalid email."), 400
    
    user = User.query.filter(User.email == email).first()
    
    if(user is None):
        return jsonify(message="Invalid credentials."), 400
    
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify(message="Invalid credentials."), 400
    
    claims = {
    "forename": user.forename,
    "surname": user.surname,
    "email": user.email,
    "role": user.role,
    }
    
    access_token = create_access_token(
    identity=user.email,
    additional_claims=claims
    )
    
    return jsonify(accessToken=access_token)

@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    email = get_jwt_identity()
    user = User.query.filter(
    User.email == email
    ).first()
    
    if user is None:
        return jsonify(message="Unknown user."), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return "",200