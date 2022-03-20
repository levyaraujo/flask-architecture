from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash


def init_app(app):
    JWTManager(app)


def encrypt(password):
    return generate_password_hash(password)
