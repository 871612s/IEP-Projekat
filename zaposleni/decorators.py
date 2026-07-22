from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_check(role):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != role:
                return jsonify(msg="Missing Authorization Header"), 401

            return fn(*args, **kwargs)

        return wrapper

    return decorator