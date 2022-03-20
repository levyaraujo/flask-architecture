from flask import Flask
from extensions import config
from extensions.models.tables import db
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    config.init_app(app)
    CORS(app)
    @app.before_first_request
    def create_db():
        db.create_all()
        return create_db

    return app
