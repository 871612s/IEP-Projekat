from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt


def role_check(role):

    def decorator(function):

        @jwt_required()
        @wraps(function)
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            if claims["role"] != role:
                return jsonify({"msg": "Unauthorized"}), 401

            return function(*args, **kwargs)

        return wrapper

    return decorator